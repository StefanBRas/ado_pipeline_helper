import pytest
from pydantic import BaseModel
from ado_pipeline_helper.utils import listify, set_if_not_none

def test_set_if_not_none_dict():
    obj = {}
    set_if_not_none(obj, 'a', 1)
    set_if_not_none(obj, 'b', None)
    assert obj == {'a': 1}

def test_set_if_not_none_BaseModel():
    class Model(BaseModel):
        a: int
        b: int
    obj = Model(a=123, b=123)
    set_if_not_none(obj, 'a', 1)
    set_if_not_none(obj, 'b', None)
    assert obj == {'a': 1, 'b': 123}

@pytest.mark.parametrize(['obj', 'expected'], [
                            ([], []),
                            ([1], [1]),
                            (1, [1]),
                            ('abc', ['abc']),
                            (['abc'], ['abc']),
                            ([[]], [[]]),
                            ]
                            )
def test_listify(obj, expected):
    new_obj = listify(obj)
    assert expected == new_obj
