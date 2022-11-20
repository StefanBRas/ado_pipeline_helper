from pathlib import Path
from typing import Any, Optional

from pydantic import BaseSettings, SecretStr

from ado_pipeline_helper.yaml_loader import yaml

CONFIG_PATH = ".ado_pipeline_helper.yml"


def get_app_config() -> dict:
    path = Path(CONFIG_PATH)
    if path.exists:
        return yaml.load(path.read_text())
    else:
        return {"pipelines": []}


class Settings(BaseSettings):
    organization: str
    project: str
    token: SecretStr

    class Config:
        env_file_encoding = "utf-8"
        fields = {
            "token": {
                "env": "AZURE_DEVOPS_EXT_PAT",
            },
        }
        config_path = ".ado_pipeline_helper.yml"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            def yaml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
                """
                A simple settings source that loads variables from a YAML file
                at the project's root.

                Here we happen to choose to use the `env_file_encoding` from Config
                when reading `.ado_pipeline_helper.yml`
                """
                encoding = settings.__config__.env_file_encoding
                path = settings.__config__.config_path
                values = yaml.load(Path(path).read_text(encoding))
                values.pop("pipelines")
                return values

            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
                file_secret_settings,
            )


class PipelineConfig(BaseSettings):
    settings: Settings
    pipeline_id: Optional[int]  # If not set, fetches from name of pipeline
    path: Path

    class Config:
        config_path = ".ado_pipeline_helper.yml"

    @classmethod
    def get_from_pipeline_local_name(cls, settings: Settings, pipeline_local_name: str):
        config_path = cls.__config__.config_path
        config = yaml.load(Path(config_path).read_text())
        pipeline = config["pipelines"][pipeline_local_name]
        return cls(settings=settings, **pipeline)
