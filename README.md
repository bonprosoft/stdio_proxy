# stdio\_proxy
[![PyPI](https://img.shields.io/pypi/v/stdio-proxy.svg)](https://pypi.org/project/stdio-proxy/)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/stdio-proxy.svg)](https://pypi.org/project/stdio-proxy/)
[![GitHub license](https://img.shields.io/github/license/bonprosoft/stdio_proxy.svg)](https://github.com/bonprosoft/stdio_proxy)
[![GitHub Actions (Tests)](https://github.com/bonprosoft/stdio_proxy/workflows/tests/badge.svg)](https://github.com/bonprosoft/stdio_proxy)


stdio\_proxy is a thread-safe library for Python 2.7 and Python 3.5+ that can temporarily redirect stdio to another objects.

## Background

Python 3.5+ has `redirect_stdout` and `redirect_stderr` in `contextlib`, that are utility functions for temporarily redirecting `sys.stdout` and `sys.stderr` to another file-like objects, respectively.
But those functions have the global side effect on `sys.stdout` and `sys.stderr`.
That means we cannot use those functions in most threaded applications.

- Python code
```py
import contextlib
import io
import time
from concurrent.futures import ThreadPoolExecutor

def run(value):
    for i in range(2):
        print("Hello from {}:{}".format(value, i))
        time.sleep(1)

def run_hook(value):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run(value)
    return buf.getvalue()

with ThreadPoolExecutor() as executor:
    f1 = executor.submit(run, "th1")
    f2 = executor.submit(run_hook, "th2")
    f1.result()
    result = f2.result()
    print("===Done===")
    print("Redirected Stdout:\n{}".format(result))
```

- What we want
```sh
Hello from th1:0
Hello from th1:1
===Done===
Redirected Stdout:
Hello from th2:0
Hello from th2:1
```

- Example of actual output
```sh
Hello from th1:0
===Done===
Redirected Stdout:
Hello from th2:0
Hello from th1:1
Hello from th2:1
```

This library aims to redirect those stdio correctly in threaded applications as well.
By just replacing `run_hook` function with the following code, the result would be exactly the same as "what we want" :)

```py
def run_hook(value):
    buf = io.BytesIO()
    with stdio_proxy.redirect_stdout(buf):
        run(value)
    return buf.getvalue()
```

## Install

```sh
$ pip install stdio-proxy
```

## Usage

- Redirect a buffer to `stdin`
```py
buf = io.BytesIO(b"foo\n")
with stdio_proxy.redirect_stdin(buf):
    print("Read: {}".format(sys.stdin.readline()))
```

- Redirect `stdout` to a buffer
```py
buf = io.BytesIO()
with stdio_proxy.redirect_stdout(buf):
    print("foo")
print("Redirected: {}".format(buf.getvalue()))
```

- Redirect `stderr` to a buffer
```py
buf = io.BytesIO()
with stdio_proxy.redirect_stderr(buf):
    sys.stderr.write("foo\n")
print("Redirected: {}".format(buf.getvalue()))
```


## License

MIT License
