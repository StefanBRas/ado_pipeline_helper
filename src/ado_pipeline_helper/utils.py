def listify(obj) -> list:
    """Makes singleton objects into lists, unless they already are.

    Yes, this only works for lists and not iterables in general.
    Why? strings.
    """
    return obj if isinstance(obj, list) else [obj]
