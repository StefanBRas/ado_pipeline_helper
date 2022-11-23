from typing import Any


def listify(obj) -> list:
    """Makes singleton objects into lists, unless they already are.

    Yes, this only works for lists and not iterables in general.
    Why? strings.
    """
    return obj if isinstance(obj, list) else [obj]

def set_if_not_none(obj: dict, key: str, val: Any) -> dict:
    if val is not None:
        obj[key] = val
    return obj
