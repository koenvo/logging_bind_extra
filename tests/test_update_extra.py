__author__ = 'koen'

import logging

from logging_bind_extra import BindExtraLogger

logging.setLoggerClass(BindExtraLogger)

mylogger = logging.getLogger("root")
mylogger.setLevel(logging.DEBUG)

class MockHandler(logging.Handler):
    def emit(self, record):
        self.record = record

handler = MockHandler()
mylogger.addHandler(handler)


class TestLogger(object):
    def test_simple(self):
        logger = logging.getLogger("root.test_simple")
        with logger.bind_extra(task_id=1):
            logger.info("some info message")

        assert handler.record.msg == "some info message"
        assert handler.record.task_id == 1

    def test_subsequential_logs(self):
        logger = logging.getLogger("root.test_simple")
        with logger.bind_extra(task_id=1):
            logger.info("some info message")

        assert handler.record.msg == "some info message"
        assert handler.record.task_id == 1

        with logger.bind_extra(task_id=2):
            logger.info("second info message")

        assert handler.record.msg == "second info message"
        assert handler.record.task_id == 2

    def test_nested(self):
        with mylogger.bind_extra(var1=1):
            logger = logging.getLogger("root.test_nested")
            with logger.bind_extra(var2=2):
                logger.error("some error message")

        assert handler.record.var1 == 1
        assert handler.record.var2 == 2

    def test_override_in_log(self):
        logger = logging.getLogger("root.test_override_in_log")
        with logger.bind_extra(var1=1, var2=2):
            logger.error("some error", extra=dict(var2=3))

        assert handler.record.var1 == 1
        assert handler.record.var2 == 3

    def test_exception_logging(self):
        logger = logging.getLogger("root.test_exception_logging")
        with logger.bind_extra(var1=1337):
            try:
                raise Exception("Exc")
            except Exception:
                logger.exception("some exception")

        assert handler.record.var1 == 1337
        assert handler.record.exc_info is not None

    def test_rollback(self):
        logger = logging.getLogger("root.test_rollback")
        with logger.bind_extra(var1=1337):
            pass

        logger.info("some msg")
        assert not hasattr(handler.record, 'var1')

    def test_as_decorator(self):
        logger = logging.getLogger("root.test_as_decorator")

        @logger.bind_extra(var1=1)
        def test():
            logger.info("some msg")

        test()
        assert handler.record.var1 == 1

    def test_as_method(self):
        logger = logging.getLogger("root.test_as_method")

        context = logger.bind_extra_enter(var1=1)
        logger.info("some msg")
        assert handler.record.var1 == 1

        context.exit()
        logger.info("some msg")
        assert not hasattr(handler.record, 'var1')