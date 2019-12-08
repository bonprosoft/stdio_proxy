import collections
import contextlib
import sys
import threading

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    from stdio_proxy.py2 import _create_proxy
elif PY3:
    from stdio_proxy.py3 import _create_proxy
else:
    raise RuntimeError("Unknown python version")

try:
    import typing

    if typing.TYPE_CHECKING:
        from typing import Dict, Iterator

        SysIO = typing.TextIO
        if PY2:
            from stdio_proxy.py2 import ThreadSafeFileObjectProxy

            ProxyIO = ThreadSafeFileObjectProxy
        elif PY3:
            from stdio_proxy.py3 import ThreadSafeTextIOWrapperProxy

            ProxyIO = ThreadSafeTextIOWrapperProxy
except ImportError:
    pass


_lock = threading.Lock()
_original = {}  # type: Dict[str, SysIO]
_proxy = {}  # type: Dict[str, ProxyIO]
_n_use = collections.defaultdict(int)  # type: Dict[str, int]


def _enter_proxy(target):
    # type: (str) -> ProxyIO
    with _lock:
        if _n_use[target] == 0:
            if target not in _original:
                original = getattr(sys, target)
                proxy = _create_proxy(original)

                _original[target] = original
                _proxy[target] = proxy
            else:
                proxy = _proxy[target]

            setattr(sys, target, proxy)

        _n_use[target] += 1
        return _proxy[target]


def _exit_proxy(target):
    # type: (str) -> None
    with _lock:
        _n_use[target] -= 1

        if _n_use[target] == 0:
            setattr(sys, target, _original[target])


@contextlib.contextmanager
def _redirect_stdio(target, new_obj, no_close=True):
    # type: (str, typing.BinaryIO, bool) -> Iterator[None]
    stdio = _enter_proxy(target)
    stdio.register(new_obj)
    try:
        yield
    finally:
        stdio.unregister()
        _exit_proxy(target)


@contextlib.contextmanager
def redirect_stdin(src_obj, no_close=True):
    # type: (typing.BinaryIO, bool) -> Iterator[None]
    """Context manager for temporarily redirecting an object to stdin.

    Note:
        For Python 3 environments, ``src_obj`` is supposed to handle ``bytes``, not ``str``.
        For Python 2 environments, ``str``, not ``unicode``.
        The easiest way to prepare ``src_obj`` for both environments is to use an ``io.BytesIO`` object.

        For Python 3 environments, the interface of ``src_obj`` should be compatible with that of ``io.BufferedReader``.
        For instance, if you use `sys.stdin.readline`, ``src_obj`` must have ``read1`` method and ``closed`` property
        that return ``bytes`` and ``bool``, respectively.

        For Python 2 environments, the interface of ``src_obj`` should be compatible with that of the Python file object.
    Examples:
        >>> with redirect_stdin(io.BytesIO(b"input_str\n")):
        ...     sys.stderr.write("Read: {}".format(sys.stdin.readline()))
        Read: input_str

    """
    with _redirect_stdio("stdin", src_obj, no_close):
        yield


@contextlib.contextmanager
def redirect_stdout(dst_obj, no_close=True):
    # type: (typing.BinaryIO, bool) -> Iterator[None]
    """Context manager for temporarily redirecting stdout to an object.

    Note:
        For Python 3 environments, ``dst_obj`` is supposed to handle ``bytes``, not ``str``.
        For Python 2 environments, ``str``, not ``unicode``.
        The easiest way to prepare ``dst_obj`` for both environments is to use an ``io.BytesIO`` object.

        For Python 3 environments, the interface of ``dst_obj`` should be compatible with that of ``io.BufferedWriter``.
        For instance, if you use `sys.stdin.readline`, ``dst_obj`` must have ``write`` method, ``flush`` method, and ``closed`` property.
        Note that the argument of ``write`` method is ``bytes``, not ``str``.

        For Python 2 environments, the interface of ``dst_obj`` should be compatible with that of the Python file object.

    Examples:
        >>> buf = io.BytesIO()
        >>> with redirect_stdout(buf):
        ...     sys.stdout.write("Foo\n")
        >>> print("Redirected: {}".format(buf.getvalue()))
        Redirected: b'Foo\n'

    """
    with _redirect_stdio("stdout", dst_obj, no_close):
        yield


@contextlib.contextmanager
def redirect_stderr(dst_obj, no_close=True):
    # type: (typing.BinaryIO, bool) -> Iterator[None]
    """Context manager for temporarily redirecting stderr to an object.

    See Also:
        redirect_stdout: Context manager for temporarily redirecting stdout to an object.
    """
    with _redirect_stdio("stderr", dst_obj, no_close):
        yield
