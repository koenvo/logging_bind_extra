# -*- coding: utf-8 -*-

from functools import wraps
from logging import Logger as BaseLogger
from copy import deepcopy

from .threadlocal import ThreadLocal
from .util import update_dict

__all__ = ["BindExtraLogger"]

_local = ThreadLocal()


class BindExtraManager(object):
    def __init__(self, **kwargs):
        self.extra = kwargs

    def __enter__(self):
        if not hasattr(_local, 'extra_binds'):
            _local.extra_binds = {}

        self.saved_extra = deepcopy(_local.extra_binds)
        update_dict(_local.extra_binds, self.extra)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _local.extra_binds.clear()
        _local.extra_binds.update(self.saved_extra)

    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            with self:
                return f(*args, **kwargs)
        return decorated


class BindExtraLogger(BaseLogger):
    def _log(self, level, msg, args, exc_info=None, extra=None):
        if extra is not None:
            extra_ = deepcopy(_local.extra_binds)
            update_dict(extra_, extra)
        else:
            extra_ = _local.extra_binds

        return super(BindExtraLogger, self)._log(level, msg, args, exc_info, extra_)

    @staticmethod
    def bind_extra(**kwargs):
        return BindExtraManager(**kwargs)