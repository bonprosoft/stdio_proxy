import contextlib
import io
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import BinaryIO, Dict, Iterator, Optional, Union

import pytest

import stdio_proxy

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


@pytest.fixture(scope="session")  # type: ignore
def fake_stdin():
    # type: () -> Iterator[None]
    if PY2:
        yield
    elif PY3:
        original = sys.stdin
        stdin = io.TextIOWrapper(io.BytesIO())
        try:
            sys.stdin = stdin
            yield
        finally:
            sys.stdin = original


def _print_test_message(msg, err_msg, n_times=5, sleep=None):
    # type: (str, str, int, Optional[float]) -> str
    read_strs = []
    for i in range(n_times):
        sys.stdout.write(msg)
        sys.stderr.write(err_msg)
        read_strs.append(sys.stdin.readline())
        if sleep is not None:
            time.sleep(sleep)

    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdin.flush()

    return "".join(read_strs)


@contextlib.contextmanager
def _hook_stdio(stdin_bytes):
    # type: (bytes) -> Iterator[Dict[str, Union[str, bytes]]]
    stdout_buffer = io.BytesIO()
    stderr_buffer = io.BytesIO()
    stdin_buffer = io.BytesIO(stdin_bytes)
    result = {
        "stdout": b"",
        "stderr": b"",
    }  # type: Dict[str, Union[str, bytes]]

    try:
        with stdio_proxy.redirect_stdin(stdin_buffer):
            with stdio_proxy.redirect_stdout(stdout_buffer):
                with stdio_proxy.redirect_stderr(stderr_buffer):
                    yield result
    finally:
        result["stdout"] = stdout_buffer.getvalue()
        result["stderr"] = stderr_buffer.getvalue()


def test_proxy(fake_stdin):
    # type: (BinaryIO) -> None
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    stdin_bytes = b"test_input"

    with _hook_stdio(stdin_bytes) as result:
        read_str = _print_test_message("test", "test_err", n_times=1)

        assert sys.stdin != original_stdin
        assert sys.stdout != original_stdout
        assert sys.stderr != original_stderr

    assert read_str == "test_input"
    assert result["stdout"] == b"test"
    assert result["stderr"] == b"test_err"
    assert sys.stdin == original_stdin
    assert sys.stdout == original_stdout
    assert sys.stderr == original_stderr


def test_multithread_proxy(fake_stdin):
    # type: (BinaryIO) -> None
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    def _run(value):
        # type: (int) -> Dict[str, Union[str, bytes]]
        input_msgs = ("{}_in\n".format(value).encode("utf-8")) * value
        with _hook_stdio(input_msgs) as result:
            assert sys.stdin != original_stdin
            assert sys.stdout != original_stdout
            assert sys.stderr != original_stderr
            read_str = _print_test_message(
                "{}\n".format(value),
                "{}_err\n".format(value),
                n_times=value,
                sleep=0.1,
            )
            result["stdin"] = read_str

        return result

    with ThreadPoolExecutor(2) as p:
        f1 = p.submit(_run, 2)
        f2 = p.submit(_run, 3)
        result1 = f1.result()
        result2 = f2.result()

    assert sys.stdin == original_stdin
    assert sys.stdout == original_stdout
    assert sys.stderr == original_stderr

    assert result1["stdin"] == "2_in\n2_in\n"
    assert result1["stdout"] == b"2\n2\n"
    assert result1["stderr"] == b"2_err\n2_err\n"

    assert result2["stdin"] == "3_in\n3_in\n3_in\n"
    assert result2["stdout"] == b"3\n3\n3\n"
    assert result2["stderr"] == b"3_err\n3_err\n3_err\n"
