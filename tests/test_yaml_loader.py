from ado_pipeline_helper.yaml_loader import YamlResolver, traverse
import pytest


def test_traverse_id_func():
    x = {"x": [1, 2, [1, 2], {"y": 1}], "z": 1}
    y = traverse(x)
    assert x == y


@pytest.mark.parametrize(
    "input, expected",
    [
        ("nothing here", "nothing here"),
        ("", ""),
        ("${{ parameters.x }}", "some_value"),
        ("prefix ${{ parameters.x }}", "prefix some_value"),
        ("${{ parameters.x }} postfix", "some_value postfix"),
        ("prefix ${{ parameters.x }} postfix", "prefix some_value postfix"),
        ("${{ parameters.x }} ${{ parameters.x }}", "some_value some_value"),
        ("${{ parameters.x }} ${{ parameters.y }}", "some_value other_value"),
    ],
)
def test_replace_parameters(input, expected):
    parameters = {"x": "some_value", "y": "other_value"}
    assert YamlResolver.replace_parameters(input, parameters) == expected
