def unique(seq):
    """
    https://stackoverflow.com/a/480227/452081
    Unique a list, but preserve order..
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def filter_dict_to_function(dict_to_filter, thing_with_kwargs):
    """
    https://stackoverflow.com/a/44052550/452081
    Filter dict so it fits the signature of a function
    """
    import inspect

    sig = inspect.signature(thing_with_kwargs)
    filter_keys = [
        param.name
        for param in sig.parameters.values()
        if param.kind == param.POSITIONAL_OR_KEYWORD
    ]
    filtered_dict = {
        filter_key: dict_to_filter[filter_key] for filter_key in filter_keys
    }
    return filtered_dict


def host_exists(data, resolver=None):
    import socket
    from databases import DatabaseURL

    if resolver == 'database-url':
        host = DatabaseURL(data).hostname
    elif callable(resolver):
        host = resolver(data)
    else:
        host = data

    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False
