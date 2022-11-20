from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, BaseSettings, SecretStr

from ado_pipeline_helper.yaml_loader import yaml

DEFAULT_CONFIG_PATH = Path(".ado_pipeline_helper.yml")
DEFAULT_PIPELINE_PATHS = [Path(path) for path in [
    "azure-pipelines.yml",
    ".azure-pipelines.yml",
]]


class PipeLineSettingsId(BaseModel):
    path: Path
    name: Optional[str]
    id: int

class PipeLineSettingsName(BaseModel):
    path: Path
    name: str
    id: Optional[int]

    @classmethod
    def from_path(cls, path: Path):
        pipeline_yaml = yaml.load(path.read_text())
        pipeline_name = pipeline_yaml.get('name')
        return cls(
            path=path,
            name=pipeline_name,
            id=None
        )


PipeLineSettings = Union[PipeLineSettingsId, PipeLineSettingsName]

class CliSettings(BaseSettings):
    organization: str
    project: str
    pipelines: dict[str, PipeLineSettings]

    @classmethod
    def read(cls, path: Path = DEFAULT_CONFIG_PATH):
        content = yaml.load(path.read_text())
        if not content.get('pipelines'):
            for pipeline_path in DEFAULT_PIPELINE_PATHS:
                if pipeline_path.exists():
                    content['pipelines'] = {
                        'default': {
                            'path': pipeline_path
                        }
                    }
        for pipeline in content['pipelines'].values():
            if pipeline.get('name') is None:
                pipeline_yaml = yaml.load(Path(pipeline['path']).read_text())
                pipeline_name = pipeline_yaml.get('name')
                if pipeline_name is not None:
                    pipeline['name'] = pipeline_name
        return cls(**content)

    def get_local_names(self) -> list[str]:
        return list(self.pipelines.keys())


class ClientSettings(BaseModel):
    organization: str
    project: str
    token: SecretStr
    pipeline_path: Path
    pipeline_id: Optional[int]  # If not set, fetches from name of pipeline
    pipeline_name: Optional[str] # TODO maybe add validator one of this two fields must be set

    @classmethod
    def from_cli_settings(cls, settings: CliSettings, pipeline_local_name:str, token: SecretStr) -> 'ClientSettings':
        pipeline = settings.pipelines[pipeline_local_name]
        return cls(
            organization = settings.organization,
            project = settings.project,
            pipeline_path= pipeline.path,
            pipeline_id=pipeline.id,
            pipeline_name=pipeline.name,
            token=token
        )
