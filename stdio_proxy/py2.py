import threading

try:
    import typing
except ImportError:
    pass

HOOK_MEMBERS = [
    "_registered_buffers",
    "_original",
    "register",
    "unregister",
    "close"]


class ThreadSafeFileObjectProxy(file):
    def __init__(self, original):
        # type: (file) -> None
        object.__setattr__(self, "_registered_buffers", threading.local())
        object.__setattr__(self, "_original", original)

    def __getattribute__(self, name):
        # type: (str) -> typing.Any
        if name in HOOK_MEMBERS:
            return object.__getattribute__(self, name)
        else:
            registered = object.__getattribute__(self, "_registered_buffers")
            buf = getattr(registered, "value", None)
            if buf is None:
                original = object.__getattribute__(self, "_original")
                return getattr(original, name)

            return getattr(buf, name)

    def __setattr__(self, name, value):
        # type: (str, typing.Any) -> typing.Any
        if name in HOOK_MEMBERS:
            raise RuntimeError("Invalid operation")
        else:
            buf = getattr(self._registered_buffers, "value", None)
            if buf is None:
                return setattr(self._original, name, value)

            return setattr(buf, name, value)

    def register(self, new_buffer, no_close=True):
        # type: (typing.BinaryIO, bool) -> None
        self._registered_buffers.value = new_buffer
        self._registered_buffers.no_close = no_close

    def unregister(self):
        # type: () -> None
        self._registered_buffers.value = None

    def close(self):
        # type: () -> None
        buf = getattr(self._registered_buffers, "value", None)
        if buf is None:
            return self._original.close()

        no_close = getattr(self._registered_buffers, "no_close", False)
        if no_close:
            buf.flush()
        else:
            buf.close()


def _create_proxy(target):
    # type: (file) -> ThreadSafeFileObjectProxy
    return ThreadSafeFileObjectProxy(target)
