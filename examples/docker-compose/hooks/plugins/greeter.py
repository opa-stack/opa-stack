from fastapi import Depends, APIRouter
from opa.core.plugin import (
    get_plugin_manager,
    PluginManager,
    Hook,
    HookDefinition,
    Setup,
)

router = APIRouter()


class name_hook(HookDefinition):
    required = True
    is_async = False
    name = 'fullname'


@router.get("/get-fullname/{firstname}/{surname}")
def show_name(
    firstname: str, surname: str, pm: PluginManager = Depends(get_plugin_manager)
):
    fullname = pm.call('fullname', firstname, surname)
    return f"Hello {fullname}"


class MyApp(Setup):
    def __init__(self, app):
        app.include_router(router)
