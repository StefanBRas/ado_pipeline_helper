from pydantic import BaseSettings, Field, SecretStr
from typing import Optional


class Settings(BaseSettings):
    organization: str
    project: str
    token: SecretStr = Field(..., env='AZURE_DEVOPS_EXT_PAT')


class PipelineConfig(BaseSettings):
    settings: Settings
    pipeline_id: Optional[int] # If not set, fetches from name of pipeline
    path: str
