import os
import re
import sys
import json
import inspect
import asyncio
import logging
import pkgutil
from collections import defaultdict
from importlib import import_module
from typing import Dict, Any, List, Callable

from fastapi import FastAPI, APIRouter

from opa.utils import unique, filter_dict_to_function
from opa import config


class BasePlugin:
    pass


class Driver(BasePlugin):
    name: str
    instance: Any = None
    opts: Dict[str, Any]
    pm: 'PluginManager'

    def __init__(self, opts=None, load='auto'):
        self.opts = opts or {}
        self.load = load

    def _pre_connection_check(self, connectionstatus, load):
        if connectionstatus == False:  # if no host found
            if self.load == 'yes':
                raise Exception(
                    f'Connect pre-check failed for {self.name}, as if the host is not there? Options {self.opts}'
                )
            else:
                return False

        if hasattr(self, 'validate'):
            return True

    def initialize(self):
        connectionstatus = self.connect()
        if self._pre_connection_check(connectionstatus, self.load):
            self.validate()

    async def initialize_async(self):
        connectionstatus = await self.connect()
        if self._pre_connection_check(connectionstatus, self.load):
            await self.validate()

    def get_instance(self):
        return self.instance


class HookDefinition(BasePlugin):
    required: bool = False
    is_async: bool = False
    _used: bool = False


class Hook(BasePlugin):
    name: str
    order: int = 0


class Setup(BasePlugin):
    ...


def get_defined_plugins(mod, plugin_types=None):
    plugin_types = plugin_types or ['hook-definitions', 'hooks', 'drivers', 'setup']
    returndata = defaultdict(list)

    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if mod.__name__ != obj.__module__:
            # We don't want to load plugins/modules if they are imported, ie 'from ... import AnotherPlugin'
            continue

        if obj is Hook or obj is Driver or obj is Setup:
            continue

        if issubclass(obj, Hook) and 'hooks' in plugin_types:
            returndata['hooks'].append(obj)
        elif issubclass(obj, HookDefinition) and 'hook-definitions' in plugin_types:
            returndata['hook-definitions'].append(obj)
        elif issubclass(obj, Driver) and 'drivers' in plugin_types:
            returndata['drivers'].append(obj)
        elif issubclass(obj, Setup) and 'setup' in plugin_types:
            returndata['setup'].append(obj)
    return returndata


class PluginManager:
    status: Dict[str, Dict]

    drivers: Dict[str, Driver]
    optional_components: Dict[str, Driver]
    hooks: Dict[str, List[Hook]]
    hook_definitions: Dict[str, Hook]

    store: Dict[str, Any]

    def __init__(self):
        self.status = defaultdict(dict)
        self.drivers = {}
        self.optional_components = {}
        self.hooks = defaultdict(list)
        self.hook_definitions = {}

        self.store = {'task_candidates': []}

    def post_hook(self):
        final_hooks: Dict[str, Hook] = {}
        for hook_name, hooks in self.hooks.items():
            definition = self.hook_definitions.get(hook_name)
            try:
                hook_to_use = sorted(hooks, key=lambda x: x.order)[-1]
            except IndexError:
                continue

            if definition:
                definition._used = True
            final_hooks[hook_name] = hook_to_use

        should_be_used = [
            name
            for name, definition in self.hook_definitions.items()
            if all([definition.required, not definition._used])
        ]
        if should_be_used:
            raise Exception(f'Hooks that should be registered: {should_be_used}')

        self.hooks = final_hooks

    def register_driver(self, driver: Driver):
        name = driver.name.lower()
        if name in self.drivers:
            if self.drivers[name] is driver:
                # This might happen example if we import a driver-class inside a plugin-file.
                # It should be valid, example if you need it for typing.
                return None
            raise Exception(
                f'Driver with this name ({name}) already exists. CaSe of driver is ignored.'
            )
        logging.debug(f'Registered driver {name}')
        self.drivers[name] = driver

    def _preload_drivers(self):
        for name, values in config.OPTIONAL_COMPONENTS.items():
            name = name.lower()
            load = values.get('LOAD', 'auto')
            if load == 'no':
                continue

            drivername = values.get('DRIVER')
            try:
                driver = self.drivers[drivername]
            except KeyError:
                raise Exception(
                    f'Invalid driver specified ({drivername}), no way to handle it'
                )

            driverinstance = driver(opts=values.get('OPTS', {}), load=load)
            driverinstance.pm = self
            self.optional_components[name] = driverinstance

            logging.info(
                f'Connecting to {name} with driver {drivername}, using {driverinstance.opts}'
            )
            yield driverinstance

    async def load_components(self):
        for driverinstance in self._preload_drivers():
            if asyncio.iscoroutinefunction(driverinstance.connect):
                await driverinstance.initialize_async()
            else:
                driverinstance.initialize()

    def load_sync_components_global(self):
        for driverinstance in self._preload_drivers():
            if asyncio.iscoroutinefunction(driverinstance.connect):
                logging.debug(f'Driver {driverinstance.name} is async, wont load')
            else:
                driverinstance.initialize()

    def register_hook_definition(self, obj):
        try:
            name = obj.name
        except AttributeError:
            name = obj.__name__

        if name in self.hook_definitions:
            raise Exception(
                f'There can only be 1 hook-definition per hook-name. "{name}" is already registered'
            )

        self.hook_definitions[name] = obj

    def register_hook(self, obj):
        try:
            name = obj.name
        except AttributeError:
            name = obj.__name__

        try:
            hook_definition = self.hook_definitions[name]
        except KeyError:
            raise Exception(
                f'There are no hook-definition for hook "{name}", are you using the correct name?'
            )

        if hook_definition.is_async:
            if not asyncio.iscoroutinefunction(obj.run):
                raise Exception(
                    f'Hook-definition is marked as async but the function is not ({obj.run}).'
                )
        else:
            if asyncio.iscoroutinefunction(obj.run):
                raise Exception(
                    f'Hook-definition is not marked as async, but is.. Mark it as async or make it sync: {obj.run}'
                )

        self.hooks[name].append(obj())

    def run_setup(self, obj, params):
        params = filter_dict_to_function(params, obj.__init__)
        name = f'{obj.__module__}.{obj.__name__}'
        self.status[name]['init'] = obj(**params)

    def call(self, name, *args, **kwargs):
        func = self.hooks[name].run
        if asyncio.iscoroutinefunction(func):
            raise Exception(
                f'The hook function ({func}) is async and should not be called using non-async calls. Call it using "await call_async()"'
            )
        return func(*args, **kwargs)

    async def call_async(self, name, *args, **kwargs):
        func = self.hooks[name].run
        if not asyncio.iscoroutinefunction(func):
            raise Exception(
                f'The hook function ({func}) is not async call it using "call(..)"'
            )

        return await self.hooks[name].run(*args, **kwargs)


def _get_plugindata():
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

    plugins_to_load = defaultdict(list)
    task_candidates = []
    routers = []

    for plugin in pkgutil.iter_modules(PLUGIN_PATHS):
        allow_match = os.path.join(plugin.module_finder.path, plugin.name)
        tasks_candidate = False

        if plugin.ispkg:
            metafile = os.path.join(allow_match, 'meta.json')

            if os.path.exists(os.path.join(allow_match, 'tasks.py')):
                tasks_candidate = True
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

        if tasks_candidate:
            task_candidates.append(plugin.name)

        defined_plugins = get_defined_plugins(mod)
        for pt in ['hook-definitions', 'hooks', 'drivers', 'setup']:
            plugins_to_load[pt] += defined_plugins[pt]
        if hasattr(mod, 'router'):
            routers.append(mod.router)

    return {
        'plugins_to_load': plugins_to_load,
        'task_candidates': task_candidates,
        'routers': routers,
    }


plugin_manager: PluginManager


async def startup(app):
    global plugin_manager
    plugin_manager = PluginManager()

    plugin_manager.store.update(**_get_plugindata())

    for hook_definition in plugin_manager.store['plugins_to_load']['hook-definitions']:
        plugin_manager.register_hook_definition(hook_definition)

    for hook in plugin_manager.store['plugins_to_load']['hooks']:
        plugin_manager.register_hook(hook)
    plugin_manager.post_hook()

    for driver in plugin_manager.store['plugins_to_load']['drivers']:
        plugin_manager.register_driver(driver)
    await plugin_manager.load_components()

    for router in plugin_manager.store['routers']:
        app.include_router(router)

    for setup in plugin_manager.store['plugins_to_load']['setup']:
        plugin_manager.run_setup(setup, {'app': app})


def startup_simple():
    """
    Startup for simple sync apps that want some of the core functionality of opa-stack,
    but not the fastapi app itself. Usefull for things like celery workers
    """
    global plugin_manager
    plugin_manager = PluginManager()

    plugin_manager.store.update(**_get_plugindata())

    for hook_definition in plugin_manager.store['plugins_to_load']['hook-definitions']:
        plugin_manager.register_hook_definition(hook_definition)

    for hook in plugin_manager.store['plugins_to_load']['hooks']:
        plugin_manager.register_hook(hook)
    plugin_manager.post_hook()

    for driver in plugin_manager.store['plugins_to_load']['drivers']:
        plugin_manager.register_driver(driver)
    plugin_manager.load_sync_components_global()


async def shutdown():
    pass


def get_plugin_manager() -> PluginManager:
    return plugin_manager


def get_component(name: str):
    try:
    return plugin_manager.optional_components[name]
    except KeyError:
        raise Exception(
            f'Component is not defined (yet?). Defined components are: {list(plugin_manager.optional_components.keys())}'
        )


def get_instance(name: str):
    return get_component(name).instance


def get_util(name: str):
    return get_component(name).util


def call_hook(name, *args, **kwargs):
    return plugin_manager.call(name, *args, **kwargs)


async def call_hook_async(name, *args, **kwargs):
    return await plugin_manager.call_async(name, *args, **kwargs)


def get_router(*args, **kwargs) -> APIRouter:
    return APIRouter(*args, **kwargs)
