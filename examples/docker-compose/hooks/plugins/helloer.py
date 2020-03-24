from fastapi import Depends, APIRouter
from opa.core.plugin import get_plugin_manager, PluginManager, BasePlugin

router = APIRouter()


@router.get("/hello")
def say_hello(pm: PluginManager = Depends(get_plugin_manager)):
    return pm.call('say_hello')


class Plugin(BasePlugin):
    hooks = {'say_hello': {'required': True}}

    def setup(self, app):
        app.include_router(router)
