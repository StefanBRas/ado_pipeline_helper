from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings, Field, SecretStr

from ado_pipeline_helper.resolver.yaml_loader import yaml

DEFAULT_CONFIG_PATH = Path(".ado_pipeline_helper.yml")


class PipeLineSettings(BaseModel):
    id: Optional[int] = None
    overrides: dict[str, str] | None = None


class CliSettingsFile(BaseSettings):
    organization: Optional[str]
    project: Optional[str]
    pipelines: dict[Path, PipeLineSettings] = Field(default_factory=dict)
    overrides: dict[str, str] | None = None

    @classmethod
    def read(cls, config_path: Path = DEFAULT_CONFIG_PATH):
        content = yaml.load(config_path.read_text())
        settings = cls(**content)
        if settings.overrides:
            for pipeline in settings.pipelines.values():
                if pipeline.overrides:
                    pipeline.overrides = settings.overrides | pipeline.overrides
        return settings


class ClientSettings(BaseModel):
    organization: str
    project: str
    token: SecretStr
    pipeline_path: Path
    pipeline_id: Optional[int]  # If not set, fetches from name of pipeline
    user: str = ""
    overrides: dict | None = None
