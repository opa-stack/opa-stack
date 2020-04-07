from opa import get_router

router = get_router()


@router.get("/hello")
def return_string():
    return 'Hello to you'
