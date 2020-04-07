from fastapi import APIRouter
from opa import call_hook, Hook, HookDefinition, get_router

router = get_router()


class name_hook(HookDefinition):
    required = True
    is_async = False
    name = 'fullname'


@router.get("/get-fullname/{firstname}/{surname}")
def show_name(firstname: str, surname: str):
    fullname = call_hook('fullname', firstname, surname)
    return f"Hello {fullname}"
