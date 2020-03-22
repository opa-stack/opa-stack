"""
Demo of using hooks to set an required hook-configuration

Hooks are placed around the codebase and a plugin can register to run when a hook is called.

Some hooks run async and some not, so they need to be defined correctly. Note that the register_hook
method are called the same way on both normal and async functions.
"""

from fastapi import Depends, APIRouter
from opa.core.plugin import get_plugin_manager, PluginManager, BasePlugin

router = APIRouter()


@router.get("/demo-hook/version", tags=["demo"])
def show_version(pm: PluginManager = Depends(get_plugin_manager)):
    # pm.call will be another place in the codebase, showing it here is just for show..
    # pm.call can be async or normal, but remember to register the correct function
    return pm.call('version')


def get_version():
    return 1


async def get_version_async():
    # You can run async code in here..
    return 2


class Plugin(BasePlugin):
    def startup(self, register_hook):
        register_hook('version', get_version)

    def setup(self, app):
        app.include_router(router)
