from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, BaseSettings, Field, SecretStr

from ado_pipeline_helper.yaml_loader import yaml

DEFAULT_CONFIG_PATH = Path(".ado_pipeline_helper.yml")


class PipeLineSettings(BaseModel):
    id: Optional[int]


class CliSettingsFile(BaseSettings):
    organization: Optional[str]
    project: Optional[str]
    pipelines: dict[Path, PipeLineSettings] = Field(default_factory=dict)

    @classmethod
    def read(cls, config_path: Path = DEFAULT_CONFIG_PATH):
        content = yaml.load(config_path.read_text())
        return cls(**content)


class ClientSettings(BaseModel):
    organization: str
    project: str
    token: SecretStr
    pipeline_path: Path
    pipeline_id: Optional[int]  # If not set, fetches from name of pipeline
    user: str = ""
