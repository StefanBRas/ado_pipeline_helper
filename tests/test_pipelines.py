from ado_pipeline_helper.client import Client, Run
from pathlib import Path
from typing import Callable
import pytest

TEST_PIPELINES = [
    (3, Path("tests/test_pipelines/test_pipeline_1.yml")),
    (4, Path("tests/test_pipelines/test_pipeline_2_extends.yml"))
]

@pytest.mark.parametrize('id_,path', TEST_PIPELINES)
def test_preview(get_client: Callable[..., Client], id_, path):
    client = get_client(id_, path)
    preview = client.preview()
    assert isinstance(preview, Run)


@pytest.mark.parametrize('id_,path', TEST_PIPELINES)
def test_validate(get_client: Callable[..., Client], id_, path):
    client = get_client(id_, path)
    preview = client.preview()
    validated = client.validate()
    with open("tmp.yml", "w") as f:
        f.write(client.load_yaml())
    assert isinstance(preview, Run)
    assert isinstance(validated, Run)
    assert validated.final_yaml == preview.final_yaml
