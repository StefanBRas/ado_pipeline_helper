from typing import Any, Union

from pydantic import BaseModel


def listify(obj) -> list:
    """Makes singleton objects into lists, unless they already are.

    Yes, this only works for lists and not iterables in general.
    Why? strings.
    """
    return obj if isinstance(obj, list) else [obj]


def set_if_not_none(
    obj: Union[dict, BaseModel], key: str, val: Any
) -> Union[dict, BaseModel]:
    if val is not None:
        if isinstance(obj, dict):  # could do some hasattr stuff here
            obj[key] = val
        else:
            setattr(obj, key, val)
    return obj


def set_if_not_none_m(
    obj: Union[dict, BaseModel], key_vals: dict[str, Any]
) -> Union[dict, BaseModel]:
    for key, val in key_vals.items():
        set_if_not_none(obj, key, val)
    return obj
