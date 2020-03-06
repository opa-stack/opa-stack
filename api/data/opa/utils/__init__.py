def unique(seq):
    """
    https://stackoverflow.com/a/480227/452081
    Unique a list, but preserve order..
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
