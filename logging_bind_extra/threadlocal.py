# -*- coding: utf-8 -*-

try:
    from greenlet import getcurrent
except ImportError:  # pragma: nocover
    from threading import local as ThreadLocal
else:  # pragma: nocover
    from weakref import WeakKeyDictionary

    class ThreadLocal(object):
        """
        threading.local() replacement for greenlets.
        """
        def __init__(self):
            self.__dict__["_weakdict"] = WeakKeyDictionary()

        def __getattr__(self, name):
            key = getcurrent()
            try:
                return self._weakdict[key][name]
            except KeyError:
                raise AttributeError(name)

        def __setattr__(self, name, val):
            key = getcurrent()
            self._weakdict.setdefault(key, {})[name] = val

        def __delattr__(self, name):
            key = getcurrent()
            try:
                del self._weakdict[key][name]
            except KeyError:
                raise AttributeError(name)
