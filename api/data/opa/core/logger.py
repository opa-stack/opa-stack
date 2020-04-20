import sys
import logging
import functools
import loguru


def log_func(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger = loguru.logger.opt(depth=1)
            if entry:
                logger.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


class InterceptHandler(logging.Handler):
    stream = sys.stderr

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def get_loglevel():
    # Level from --log-level when using uvicorn
    # If uvicorn doesnt define a level, the logger default (root logger) is
    # used, which is WARNING
    return logging.getLogger('uvicorn').getEffectiveLevel()


def get_logformat(record):
    if 'var' in record['extra']:
        return loguru._defaults.LOGURU_FORMAT + ' {extra[var]}\n'
    return loguru._defaults.LOGURU_FORMAT + '\n'


class LogHandler:
    def __ror__(self, obj):
        if isinstance(obj, dict):
            logger = loguru.logger.bind(var=obj)
        else:
            logger = loguru.logger.bind(
                var={'str': str(obj), '__repr__': repr(obj), 'type': type(obj)}
            )

        logger.opt(depth=1, ansi=True).debug('<yellow>Object</yellow>')
        return obj

    def __call__(self, *args, **kwargs):
        return getattr(loguru.logger.opt(depth=1), self.level)(*args, **kwargs)

    def __getattr__(self, level):
        handler = LogHandler()
        handler.level = level
        return handler

    def setup(self):
        loguru.logger.remove()
        loguru.logger.add(sys.stdout, format=get_logformat, level=get_loglevel())
        loguru.logger.bind(request_id='app')
        logging.basicConfig(handlers=[InterceptHandler()], level=0)

        # Can be removed when https://github.com/encode/uvicorn/issues/630 is fixed?
        # Also see https://github.com/Delgan/loguru/issues/247
        logging.getLogger().handlers = [InterceptHandler()]


log = LogHandler()
log.setup()
