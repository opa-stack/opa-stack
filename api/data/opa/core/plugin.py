import os
import re
import sys
import json
import logging
import pkgutil
from importlib import import_module
from typing import Dict, Any, List, Callable

from fastapi import FastAPI

from opa.utils import unique, filter_dict_to_function
from opa import config


class BasePlugin:
    pass


class Component:
    instance = None
    hooks: Dict[str, dict]

    def get(self):
        return self.instance


import asyncio

from collections import defaultdict


class PluginManager:
    status: Dict[str, Dict]
    setup_queue: List[Dict[str, Any]]

    component_drivers: Dict[str, Component]
    optional_components: Dict[str, Component]

    hooks: Dict[str, Dict]
    _temp_hook_funcs: Dict[str, Callable]

    def __init__(self):
        self.status = defaultdict(dict)
        self.setup_queue = []
        self.component_drivers = {}
        self.optional_components = {}

        """
        Each hook have multiple options, those are.
          * required: True|False, if app-start should fail if it is missing.
        """
        self.hooks = {'version': {}}

        self._temp_hook_funcs = {}

    def post_hook_registrations(self):
        self.finish_hook_registration()
        self.check_invalid_hooks()
        self.check_required_hooks()

    def finish_hook_registration(self):
        for name in self.hooks.keys():
            if name in self._temp_hook_funcs:
                self.hooks[name]['func'] = self._temp_hook_funcs[name]

    def check_required_hooks(self):
        missing = []
        for hookname, config in self.hooks.items():
            if config.get('required'):
                if not callable(config.get('func')):
                    missing.append(hookname)
        if missing:
            raise Exception(f'Missing required hooks: {missing}')

    def check_invalid_hooks(self):
        for hookname in self._temp_hook_funcs:
            if not hookname in self.hooks:
                raise Exception(f'Hook "{hookname}" is not registered for use.')

    def register_driver(self, name: str, component: Component):
        name = name.lower()
        if name in self.component_drivers:
            raise Exception(
                f'Driver with this name ({name}) already exists. CaSe of driver is ignored.'
            )
        logging.debug(f'Registered driver {name}')
        self.component_drivers[name] = component

    async def load_components(self):
        """
        Preload the components that we are going to use.
        The components will be available using singletons that represent connections.
        We will therefor reuse each components connection and connect once per
        definition in config.OPTIONAL_COMPONENTS
        """
        for name, values in config.OPTIONAL_COMPONENTS.items():
            name = name.lower()
            load = values.get('LOAD', 'auto')
            if load == 'no':
                continue

            drivername = values.get('DRIVER')
            try:
                driver = self.component_drivers[drivername]
            except KeyError:
                raise Exception(
                    f'Invalid driver specified ({drivername}), no way to handle it'
                )

            driverinstance = driver()

            if asyncio.iscoroutinefunction(driverinstance.connect):
                await driverinstance.connect(opts=values.get('OPTS', {}))
            else:
                connection_status = driverinstance.connect(opts=values.get('OPTS', {}))
            self.optional_components[name] = driverinstance

    def add_hooks(self, hooks):
        for k, v in hooks.items():
            if k in self.hooks:
                raise Exception(f'Hook "{k}" can only be added once')
            logging.debug(f'Adding hook {k} with data {v}')
            self.hooks[k] = v

    def register_hook(self, name, func):
        if name in self._temp_hook_funcs:
            raise Exception(f'Hook "{name}" is already handled')

        self._temp_hook_funcs[name] = func

    def run_setup_queue(self, app):
        for plugin in self.setup_queue:
            if hasattr(plugin['obj'], 'setup'):
                logging.debug('Plugin had a setup function, running')
                params = filter_dict_to_function({'app': app}, plugin['obj'].setup)
                self.status[plugin['name']]['setup'] = plugin['obj'].setup(**params)

    def call(self, name, *args, **kwargs):
        return self.hooks[name]['func'](*args, **kwargs)

    async def call_async(self, name, *args, **kwargs):
        return await self.hooks[name]['func'](*args, **kwargs)


plugin_manager: PluginManager


async def startup():
    global plugin_manager
    plugin_manager = PluginManager()  # Singleton used around the app

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

        if not hasattr(mod, 'Plugin'):
            # Might just be some helper utilities wanted
            continue

        obj = mod.Plugin()

        plugin_manager.setup_queue.append({'obj': obj, 'name': plugin.name})

        if hasattr(obj, 'hooks'):
            plugin_manager.add_hooks(obj.hooks)

        if hasattr(obj, 'startup'):
            plugin_manager.status[plugin.name]['startup'] = obj.startup(
                **filter_dict_to_function(
                    {
                        'register_hook': plugin_manager.register_hook,
                        'register_driver': plugin_manager.register_driver,
                    },
                    obj.startup,
                )
            )

    await plugin_manager.load_components()
    plugin_manager.post_hook_registrations()


async def shutdown():
    pass


def setup(app):
    plugin_manager.run_setup_queue(app)


def get_plugin_manager() -> PluginManager:
    return plugin_manager


def get_component(name):
    """
    Returns a function to get a component
    """

    def inner():
        try:
            return plugin_manager.optional_components[name]
        except KeyError:
            raise Exception(
                f'Invalid component "{name}", valid components are: {list(plugin_manager.optional_components.keys())}'
            )

    return inner
