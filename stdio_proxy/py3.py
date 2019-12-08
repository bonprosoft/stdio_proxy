import _pyio  # type: ignore
import threading
from typing import BinaryIO, TextIO


class ThreadSafeTextIOWrapperProxy(_pyio.TextIOWrapper):
    def __init__(self, *args, **kwargs):
        self._registered_buffers = threading.local()
        super(ThreadSafeTextIOWrapperProxy, self).__init__(*args, **kwargs)

    def register(self, new_buffer, no_close=True):
        # type: (BinaryIO, bool) -> None
        self._registered_buffers.value = new_buffer
        self._registered_buffers.no_close = no_close

    def unregister(self):
        # type: () -> None
        self._registered_buffers.value = None

    @property
    def buffer(self):
        # type: () -> BinaryIO
        buf = getattr(self._registered_buffers, "value", None)
        if buf is None:
            return self._buffer

        return buf

    def close(self):
        # type: () -> None
        no_close = getattr(self._registered_buffers, "no_close", False)
        if no_close:
            self.buffer.flush()
        else:
            super(ThreadSafeTextIOWrapperProxy, self).close()

    def write(self, s):
        # type: (str) -> None
        return super(ThreadSafeTextIOWrapperProxy, self).write(s)


def _create_proxy(target):
    # type: (TextIO) -> ThreadSafeTextIOWrapperProxy
    return ThreadSafeTextIOWrapperProxy(
        target.buffer,
        target.encoding,
        getattr(target, "errors", "strict"),
        getattr(target, "newlines", None),
        getattr(target, "line_buffering", True),
    )
