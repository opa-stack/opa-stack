import json
import logging
from dynaconf import LazySettings

config = LazySettings(
    ENV_SWITCHER_FOR_DYNACONF='ENV',
    ENVVAR_PREFIX_FOR_DYNACONF='OPA',
    ROOT_PATH_FOR_DYNACONF='/data/settings',
    INCLUDES_FOR_DYNACONF=[
        '/data/opa/default-settings.yaml',
        '*.yaml',
        '*.json',
        '*.py',
        '*.ini',
        '*.toml',
    ],
)

logging.debug(f'Using configuration environemnt={config.ENV_FOR_DYNACONF}')
logging.debug('Configuration is:')
logging.debug(json.dumps(config.as_dict(internal=False), indent=2))
