import pytest
from pydantic import SecretStr
from typing import Iterable, Dict
from ado_pipeline_helper import ClientSettings, Client
from pathlib import Path


@pytest.fixture
def client():
    personal_access_token = "rvg2pydxvliujhijmcjpmb5kh7sicjefq6sby5iav7ncwwxu5xdq"
    settings = ClientSettings(
        organization="sbras",
        project="pypeline",
        token=SecretStr(personal_access_token),
        pipeline_id=3,
        pipeline_path=Path("tests/test_pipelines/test_pipeline_1.yml"),
        pipeline_name=None
    )
    yield Client.from_client_settings(settings)


test_pipeline_dir = Path(__file__).parent.joinpath("test_pipeline")


@pytest.fixture
def pipeline_paths() -> Iterable[list[Path]]:
    yield list(test_pipeline_dir.glob("test_pipeline_*.yml"))


@pytest.fixture
def pipelines_content(pipeline_paths: list[Path]) -> Iterable[Dict[str, str]]:
    yield {str(path): path.read_text() for path in pipeline_paths}
