import re
import os
from typing import Union

from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings, Secret
from databases import DatabaseURL


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1", "YES")
    return result


load_dotenv(".env")

PROJECT_NAME = os.getenv("PROJECT_NAME", "opa-stack")
PROJECT_DESCRIPTION = os.getenv("PROJECT_DESCRIPTION", "")

PLUGIN_PATHS = list(CommaSeparatedStrings(os.getenv("PLUGIN_PATHS", ""))) + [
    "/data/opa/plugins",
]
PLUGIN_WHITELIST_RE = re.compile(os.getenv("PLUGIN_WHITELIST_RE", ""))
PLUGIN_WHITELIST_LIST = CommaSeparatedStrings(os.getenv("PLUGIN_WHITELIST_LIST", ""))
PLUGIN_BLACKLIST_LIST = CommaSeparatedStrings(os.getenv("PLUGIN_BLACKLIST_LIST", ""))
PLUGIN_BLACKLIST_RE = re.compile(os.getenv("PLUGIN_BLACKLIST_RE", ""))


ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", "*"))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "secret-key"))

MONGODB_URL_ENV = os.getenv("MONGODB_URL", "")
if not MONGODB_URL_ENV:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_USER", "mongo")
    MONGO_PASS = os.getenv("MONGO_PASSWORD", "mongo")
    MONGO_DB = os.getenv("MONGO_DB", "api")

    MONGODB_URL = DatabaseURL(
        f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
    )
else:
    MONGODB_URL = DatabaseURL(MONGODB_URL_ENV)

database_name = MONGO_DB

if os.getenv('BETTER_EXCEPTIONS'):
    better_exception_length = str(os.getenv('BETTER_EXCEPTIONS_MAX_LENGTH', ''))

    if better_exception_length:
        import better_exceptions

        better_exception_length_val: Union[int, None]

        try:
            better_exception_length_val = int(better_exception_length)
        except (TypeError, ValueError):
            better_exception_length_val = None
        better_exceptions.MAX_LENGTH = better_exception_length_val
