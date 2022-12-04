from pathlib import Path
from typing import Callable

import pytest

from ado_pipeline_helper.client import Client, Run

TEST_PIPELINES = [
    (Path("tests/test_pipelines/test_pipeline_1.yml"), 3),
    (Path("tests/test_pipelines/test_pipeline_2_extends.yml"), 4),
    (Path("tests/test_pipelines/test_pipeline_3_nested_templates.yml"), 7),
    (Path("tests/test_pipelines/test_pipeline_4_parameters.yml"), 8),
    (Path("tests/test_pipelines/test5variable.yml"), 9),
]


@pytest.mark.parametrize("path,id_", TEST_PIPELINES)
def test_preview(get_client: Callable[..., Client], id_, path):
    client = get_client(id_, path)
    preview = client.preview()
    assert isinstance(preview, Run)


@pytest.mark.parametrize("path,id_", TEST_PIPELINES)
def test_validate(get_client: Callable[..., Client], id_, path):
    client = get_client(id_, path)
    preview = client.preview()
    validated = client.validate()
    assert isinstance(preview, Run)
    assert isinstance(validated, Run)
    assert validated.final_yaml == preview.final_yaml

