import os

from opa.core import config

if config.BETTER_EXCEPTIONS:
    import better_exceptions

    better_exceptions.MAX_LENGTH = config.get('BETTER_EXCEPTIONS_MAX_LENGTH', 400)
    better_exceptions.hook()

if config.PTVSD:
    import ptvsd

    ptvsd.enable_attach(('0.0.0.0', 5678), redirect_output=True)
