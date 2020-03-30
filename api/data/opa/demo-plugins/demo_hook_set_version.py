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


class version(HookDefinition):
    required = True


@router.get("/demo-hook/version", tags=["demo"])
def show_version(pm: PluginManager = Depends(get_plugin_manager)):
    # pm.call will be another place in the codebase, showing it here is just for show..
    # pm.call can be async or normal, but remember to register the correct function
    return pm.call('version')


class hook_sync(Hook):
    name = 'version'

    def run(self):
        return 1


class hook_async(Hook):
    name = 'version'

    async def run(self):
        # You can run async code in here..
        return 2


class Demo(Setup):
    def __init__(self, app):
        app.include_router(router)
