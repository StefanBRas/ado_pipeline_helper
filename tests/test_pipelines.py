from pathlib import Path
from typing import Callable

import pytest

from ado_pipeline_helper.client import Client, Run

TEST_PIPELINES = [
    (Path("tests/test_pipelines/test_pipeline_1.yml"), 3),
    (Path("tests/test_pipelines/test_pipeline_2_extends.yml"), 4),
    (Path("tests/test_pipelines/test_pipeline_3_nested_templates.yml"), 7),
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
    print(str(preview.final_yaml))
    print(client.load_yaml())
    validated = client.validate()
    assert isinstance(preview, Run)
    assert isinstance(validated, Run)
    assert validated.final_yaml == preview.final_yaml
