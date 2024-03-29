import os
from pathlib import Path
from typing import Dict, Iterable

import pytest
from pydantic import SecretStr

from ado_pipeline_helper import Client, ClientSettings
from ado_pipeline_helper.cli import TOKEN_ENV_VAR

# test_pipeline_dir = Path(__file__).parent.joinpath("test_pipelines")
# pipelines =  test_pipeline_dir.glob("test_pipeline_*.yml")


@pytest.fixture
def get_client():
    personal_access_token = os.environ[TOKEN_ENV_VAR]

    overrides = {
        "${{ coalesce('','templates/stages/simple2.yml')}}": "templates/stages/simple2.yml"
    }

    def _get_client(id_, path):
        settings = ClientSettings(
            organization="sbras",
            project="pypeline",
            token=SecretStr(personal_access_token),
            pipeline_id=id_,
            pipeline_path=path,
            user="stefan-bruhn",
            overrides=overrides,
        )
        return Client.from_client_settings(settings)

    yield _get_client


@pytest.fixture
def pat_env():
    old = os.environ.get(TOKEN_ENV_VAR)
    personal_access_token = "2wufmwjcskh27dwgg3endnog53lzi54ejniciv5wrpts3vuv3vkq"
    os.environ[TOKEN_ENV_VAR] = personal_access_token
    yield
    if old is not None:
        os.environ[TOKEN_ENV_VAR] = old


test_pipeline_dir = Path(__file__).parent.joinpath("test_pipeline")


@pytest.fixture
def pipeline_paths() -> Iterable[list[Path]]:
    yield list(test_pipeline_dir.glob("test_pipeline_*.yml"))


@pytest.fixture
def pipelines_content(pipeline_paths: list[Path]) -> Iterable[Dict[str, str]]:
    yield {str(path): path.read_text() for path in pipeline_paths}
