"""
Demo of using hooks to set an required hook-configuration

Hooks are placed around the codebase and a plugin can register to run when a hook is called.
"""

from fastapi import Depends, APIRouter
from opa.core.plugin import (
    get_plugin_manager,
    PluginManager,
    Hook,
    HookDefinition,
    Setup,
)

router = APIRouter()


class async_version(HookDefinition):
    required = True
    is_async = True
    name = 'async-version'


class sync_version(HookDefinition):
    required = True
    name = 'sync-version'


@router.get("/demo-hook/version", tags=["demo"])
async def show_version(pm: PluginManager = Depends(get_plugin_manager)):
    async_version = await pm.call_async('async-version')
    sync_version = pm.call('sync-version')
    return {'sync-version': sync_version, 'async-version': async_version}


class hook_sync(Hook):
    name = 'sync-version'

    def run(self):
        return 1


class hook_async_a(Hook):
    name = 'async-version'
    order = 2

    async def run(self):
        return 2


class hook_async_b(Hook):
    name = 'async-version'
    order = 2

    async def run(self):
        return 3


class Demo(Setup):
    def __init__(self, app):
        app.include_router(router)
