import _pyio
import threading
from typing import BinaryIO, Optional, TextIO, Tuple


class ThreadSafeTextIOWrapperProxy(_pyio.TextIOWrapper):  # type: ignore
    def __init__(self, *args, **kwargs):  # type: ignore
        self._local_objects = threading.local()
        super(ThreadSafeTextIOWrapperProxy, self).__init__(*args, **kwargs)

    def register(self, new_buffer, no_close=True):
        # type: (BinaryIO, bool) -> None
        self._local_objects.buffer = new_buffer
        self._local_objects.no_close = no_close
        self._local_objects.decoded_chars = ""
        self._local_objects.decoded_chars_used = 0
        self._local_objects.snapshot = None
        self._local_objects.registered = True

    def unregister(self):
        # type: () -> None
        self._local_objects.buffer = None
        self._local_objects.registered = False

    @property
    def _registered(self):
        # type: () -> bool
        return getattr(self._local_objects, "registered", False)

    @property
    def _decoded_chars(self):
        # type: () -> bytes
        """buffer for text returned from decoder"""
        if not self._registered:
            return super(ThreadSafeTextIOWrapperProxy, self).__dict__[
                "_decoded_chars"
            ]
        else:
            return self._local_objects.decoded_chars

    @_decoded_chars.setter
    def _decoded_chars(self, value):
        # type: (bytes) -> None
        if not self._registered:
            super(ThreadSafeTextIOWrapperProxy, self).__dict__[
                "_decoded_chars"
            ] = value
        else:
            self._local_objects.decoded_chars = value

    @property
    def _decoded_chars_used(self):
        # type: () -> int
        """offset into _decoded_chars for read()"""
        if not self._registered:
            return super(ThreadSafeTextIOWrapperProxy, self).__dict__[
                "_decoded_chars_used"
            ]
        else:
            return self._local_objects.decoded_chars_used

    @_decoded_chars_used.setter
    def _decoded_chars_used(self, value):
        # type: (int) -> None
        if not self._registered:
            super(ThreadSafeTextIOWrapperProxy, self).__dict__[
                "_decoded_chars_used"
            ] = value
        else:
            self._local_objects.decoded_chars_used = value

    @property
    def _snapshot(self):
        # type: () -> Optional[Tuple[int, bytes]]
        """info for reconstructing decoder state"""
        if not self._registered:
            return super(ThreadSafeTextIOWrapperProxy, self).__dict__[
                "_snapshot"
            ]
        else:
            return self._local_objects.snapshot

    @_snapshot.setter
    def _snapshot(self, value):
        # type: (Optional[Tuple[int, bytes]]) -> None
        if not self._registered:
            super(ThreadSafeTextIOWrapperProxy, self).__dict__[
                "_snapshot"
            ] = value
        else:
            self._local_objects.snapshot = value

    @property
    def buffer(self):
        # type: () -> BinaryIO
        if not self._registered:
            return self._buffer

        buf = self._local_objects.buffer
        assert buf is not None
        return buf

    def close(self):
        # type: () -> None
        if self._registered and self._local_objects.no_close:
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
