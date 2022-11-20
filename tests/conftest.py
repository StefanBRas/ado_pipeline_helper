import pytest
from pydantic import SecretStr
from typing import Iterable, Dict
from ado_pipeline_helper import Config, Client
from pathlib import Path

@pytest.fixture
def config():
    personal_access_token = "rvg2pydxvliujhijmcjpmb5kh7sicjefq6sby5iav7ncwwxu5xdq"
    yield Config(organization="sbras", project="pypeline",
                              pipeline_id=3,
                              token = SecretStr(personal_access_token),
                              path="tests/test_pipelines/test_pipeline_1.yml"
                              )

@pytest.fixture
def client(config):
    yield Client(config)

test_pipeline_dir = Path(__file__).parent.joinpath("test_pipeline")

@pytest.fixture
def pipeline_paths() -> Iterable[list[Path]]:
    yield list(test_pipeline_dir.glob("test_pipeline_*.yml"))

@pytest.fixture
def pipelines_content(pipeline_paths: list[Path]) -> Iterable[Dict[str, str]]:
    yield {str(path): path.read_text()  for path in pipeline_paths}

