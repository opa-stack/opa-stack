import os
import sys
import logging
import pkgutil
from importlib import import_module

from fastapi import FastAPI

from ..core.config import PLUGIN_PATHS, PLUGIN_ALLOWED


class PluginManager:
    def __init__(self):
        """
        Hook-definitions, ie, valid hooks and their config

        Each hook have multiple options, those are.
          * required: True|False, if app-start should fail if it is missing.
          * mode: one of
            * IMMUTABLE: Hook can only be set once, it can not be overwritten.
        """
        self.hooks = {'version': {'required': True, 'mode': 'IMMUTABLE'}}

    def check_required(self):
        missing = []
        for hookname, config in self.hooks.items():
            if config.get('required'):
                if not callable(config.get('func')):
                    missing.append(hookname)
        if missing:
            raise Exception(f'Missing required hooks: {missing}')

    def register_hook(self, name, func):
        if name not in self.hooks:
            raise Exception(f'Invalid plugin hook "{name}", see docs for valid hooks.')

        if (
            self.hooks[name].get('mode') == 'IMMUTABLE'
            and self.hooks[name].get('func') is not None
        ):
            raise Exception(
                f'Hook {name} is already occupied and it is marked as IMMUTABLE'
            )

        self.hooks[name]['func'] = func

    def call(self, name, *args, **kwargs):
        return self.hooks[name]['func'](*args, **kwargs)

    async def call_async(self, name, *args, **kwargs):
        return await self.hooks[name]['func'](*args, **kwargs)


plugin_manager = PluginManager()  # Singleton used around the app


def initialize(app):
    """
    Plugins are imported from multiple paths with these rules:
      * First with a unique name wins
      * Plugin must also be in PLUGIN_ALLOWED (regex)
    """

    logging.info(f'plugin-paths: {PLUGIN_PATHS}, regex-check: {PLUGIN_ALLOWED}')

    sys.path += PLUGIN_PATHS

    for plugin in pkgutil.iter_modules(PLUGIN_PATHS):
        allow_match = os.path.join(plugin.module_finder.path, plugin.name)
        logging.debug(f'Checking if "{allow_match}" is a match')
        load = True if PLUGIN_ALLOWED.match(allow_match) else False
        logging.info(
            f'Plugin: {plugin.name} (match_check: {allow_match}) (loading: {load})'
        )

        if not load:
            continue

        mod = import_module(plugin.name)

        if hasattr(mod, 'setup'):
            logging.debug('Plugin had a setup function, running')
            # There might exists utils plugins, that are there only to expose fuctions or classes to others
            mod.setup(register_hook=plugin_manager.register_hook, app=app)

    plugin_manager.check_required()


def get_plugin_manager() -> PluginManager:
    logging.info('get_plugin_manager')
    return plugin_manager
