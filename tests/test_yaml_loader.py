from ado_pipeline_helper.yaml_loader import YamlResolver, traverse, yaml
import pytest

def test_traverse():
    x = {'x': [1,2,[1,2], {'y': 1}], 'z': 1}
    y = traverse(x)
    assert x == y

def test_traverse_mod():
    def dict_func(val):
        if isinstance(val, dict) and 'template' in val.keys():
            return {'z': 1, 'w': 2}
        if isinstance(val, str) and '${{ x }}' in val:
            return 'NEW_VALUE'
        return None
    x = {'template': 'a'}
    y = traverse(x, mod_func=dict_func)
    assert y == {'z': 1, 'w': 2}
    x = {'a': " adssad ${{ x }}"}
    y = traverse(x, mod_func=dict_func)
    assert y == {'a': 'NEW_VALUE'}


@pytest.mark.parametrize('input, expected',[
                              ("nothing here", "nothing here"),
                              ("", ""),
                              ("${{ parameters.x }}", "some_value"),
                              ("prefix ${{ parameters.x }}", "prefix some_value"),
                              ("${{ parameters.x }} postfix", "some_value postfix"),
                              ("prefix ${{ parameters.x }} postfix", "prefix some_value postfix"),
                              ("${{ parameters.x }} ${{ parameters.x }}", "some_value some_value"),
                              ("${{ parameters.x }} ${{ parameters.y }}", "some_value other_value"),
                          ]
                          )
def test_replace_parameters(input, expected):
    parameters = {
        'x': "some_value",
        'y': "other_value"
    }
    assert YamlResolver.replace_parameters(input, parameters) == expected

