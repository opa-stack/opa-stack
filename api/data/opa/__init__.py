import sys
import json

from typing import Dict
from dynaconf import LazySettings

from opa.core.logger import log

config = LazySettings()

from opa.core.plugin import (
    HookDefinition,
    Hook,
    Driver,
    Setup,
    get_plugin_manager,
    get_component,
    get_instance,
    get_router,
    call_hook,
    call_hook_async,
)


def init_configuration():
    config.configure(
        ENV_SWITCHER_FOR_DYNACONF='ENV',
        ENVVAR_PREFIX_FOR_DYNACONF='OPA',
        ROOT_PATH_FOR_DYNACONF='/data/settings',
        INCLUDES_FOR_DYNACONF=[
            '/data/build-info-container.json',
            '/data/opa/default-settings.yaml',
            '*.yaml',
            '*.json',
            '*.py',
            '*.ini',
            '*.toml',
            '/data/opa/tests/settings/*.yaml',
        ],
    )

    log.debug(f'Using configuration environemnt={config.ENV_FOR_DYNACONF}')
    log.debug('Configuration is:')
    log.debug(json.dumps(config.as_dict(internal=False), indent=2))


state: Dict = {}
