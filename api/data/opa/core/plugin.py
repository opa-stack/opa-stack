import os
import re
import sys
import json
import logging
import pkgutil
from importlib import import_module

from fastapi import FastAPI

from opa.utils import unique
from opa import config


class PluginManager:
    def setup(self):
        """
        Hook-definitions, ie, valid hooks and their config

        Each hook have multiple options, those are.
          * required: True|False, if app-start should fail if it is missing.
          * mode: one of
            * IMMUTABLE: Hook can only be set once, it can not be overwritten.
        """
        self.hooks = {'version': {'mode': 'IMMUTABLE'}}

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


def init(app):
    plugin_manager.setup()

    """
    Plugins are imported from multiple paths with these rules:
      * First with a unique name wins
      * There are multiple matchers, that ALL must return true. They return true if they are NOT set, or if they match "$plugin_path / $plugin_name"
        * PLUGIN_WHITELIST_RE (regex)
        * PLUGIN_WHITELIST_LIST
        * PLUGIN_WHITELIST_TAGS
        * not in PLUGIN_BLACKLIST_LIST
        * not in PLUGIN_BLACKLIST_RE
        * not in PLUGIN_BLACKLIST_TAGS
    """
    PLUGIN_WHITELIST_RE = re.compile(config.PLUGIN_WHITELIST_RE)
    PLUGIN_BLACKLIST_RE = re.compile(config.PLUGIN_BLACKLIST_RE)

    PLUGIN_WHITELIST_TAGS = set(config.PLUGIN_WHITELIST_TAGS)
    PLUGIN_BLACKLIST_TAGS = set(config.PLUGIN_BLACKLIST_TAGS)

    PLUGIN_PATHS = unique(
        list([config.PLUGIN_PATHS])
        if isinstance(config.PLUGIN_PATHS, str)
        else config.PLUGIN_PATHS
    ) + ['/data/opa/plugins']

    logging.info(
        'Plugin loading settings:'
        f'  plugin-paths: {PLUGIN_PATHS}\n'
        f'  whitelist-regex: {PLUGIN_WHITELIST_RE}\n'
        f'  whitelist-list: {config.PLUGIN_WHITELIST_LIST}\n'
        f'  whitelist-tags: {config.PLUGIN_WHITELIST_TAGS}\n'
        f'  blacklist-list: {config.PLUGIN_BLACKLIST_LIST}\n'
        f'  blacklist-regex: {PLUGIN_BLACKLIST_RE}\n'
        f'  blacklist-tags: {PLUGIN_BLACKLIST_TAGS}\n'
    )

    sys_paths = sys.path + PLUGIN_PATHS
    sys.path = unique(sys_paths)

    for plugin in pkgutil.iter_modules(PLUGIN_PATHS):
        allow_match = os.path.join(plugin.module_finder.path, plugin.name)

        if plugin.ispkg:
            metafile = os.path.join(allow_match, 'meta.json')
        else:
            metafile = f'{allow_match}-meta.json'

        logging.debug('')
        logging.debug(f'Checking if we should load "{allow_match}"')

        if os.path.exists(metafile):
            logging.debug(f'Found metafile @ {metafile}')
            metadata = json.load(open(metafile, 'r'))
        else:
            logging.debug(f'Metafile @ {metafile} does not exist, using empty metadata')
            metadata = {}
        logging.debug(f'Metadata: {metadata}')

        load_checks = {}

        if config.PLUGIN_WHITELIST_LIST:
            load_checks['PLUGIN_WHITELIST_LIST'] = (
                allow_match in config.PLUGIN_WHITELIST_LIST
            )

        if PLUGIN_WHITELIST_RE.pattern:
            load_checks['PLUGIN_WHITELIST_RE'] = bool(
                PLUGIN_WHITELIST_RE.match(allow_match)
            )

        if PLUGIN_WHITELIST_TAGS:
            load_checks['PLUGIN_WHITELIST_TAGS'] = bool(
                PLUGIN_WHITELIST_TAGS & set(metadata.get('tags', []))
            )

        if config.PLUGIN_BLACKLIST_LIST:
            load_checks['PLUGIN_BLACKLIST_LIST'] = (
                allow_match not in config.PLUGIN_BLACKLIST_LIST
            )

        if PLUGIN_BLACKLIST_RE.pattern:
            load_checks['PLUGIN_BLACKLIST_RE'] = not bool(
                PLUGIN_BLACKLIST_RE.match(allow_match)
            )

        if PLUGIN_BLACKLIST_TAGS:
            load_checks['PLUGIN_BLACKLIST_TAGS'] = not bool(
                PLUGIN_BLACKLIST_TAGS & set(metadata.get('tags', []))
            )

        load = all(load_checks.values())
        logging.debug(f'Load-checks: {load_checks}, overall({load})')

        if not load:
            continue

        logging.info(f'Loading plugin: {plugin.name}')
        mod = import_module(plugin.name)

        if hasattr(mod, 'setup'):
            logging.debug('Plugin had a setup function, running')
            # There might exists utils plugins, that are there only to expose fuctions or classes to others
            mod.setup(register_hook=plugin_manager.register_hook, app=app)

    plugin_manager.check_required()


def get_plugin_manager() -> PluginManager:
    return plugin_manager
