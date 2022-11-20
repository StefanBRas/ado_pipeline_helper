from pydantic import BaseModel, SecretStr
from azure.devops.connection import Connection
from azure.devops.v6_0.pipelines.models import Run
from azure.devops.exceptions import AzureDevOpsServiceError
from msrest.authentication import BasicAuthentication
from ado_pipeline_helper.yaml_loader import YamlResolver
from typing import Optional
from pathlib import Path


class Config(BaseModel):
    organization: str
    project: str
    pipeline_id: int
    token: SecretStr
    path: str

class PipelineValidationError(Exception):
    pass

class Client:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.pipeline_client = self._get_pipeline_client(config)

    def _get_pipeline_client(self, config: Config):
        credentials = BasicAuthentication('', config.token.get_secret_value())
        organization_url = f'https://dev.azure.com/{config.organization}'
        connection = Connection(base_url=organization_url, creds=credentials)
        return connection.clients_v6_0.get_pipelines_client()

    def load_yaml(self) -> str:
        resolver = YamlResolver(Path(self._config.path))
        return resolver.get_yaml()

    def _call_run_pipeline_endpoint(self, run_parameters: Optional[dict]=None) -> Run | str:
        try:
            return self.pipeline_client.run_pipeline(
                pipeline_id=self._config.pipeline_id,
                project=self._config.project,
                run_parameters=run_parameters if run_parameters is not None else {}
            )
        except AzureDevOpsServiceError as e:
            return e.message
        

    def validate(self) -> Run | str:
        run_parameters={
                    "preview_run": True,
                    "yamlOverride": self.load_yaml() 
                }
        return self._call_run_pipeline_endpoint(run_parameters)

    def run(self) -> Run | str:
        return self._call_run_pipeline_endpoint()

    def preview(self) -> Run | str:
        run_parameters={
                    "preview_run": True,
                }
        return self._call_run_pipeline_endpoint(run_parameters)


if __name__ == "__main__":
    personal_access_token = "rvg2pydxvliujhijmcjpmb5kh7sicjefq6sby5iav7ncwwxu5xdq"
    config = Config(organization="sbras", project="pypeline",
                              pipeline_id=1,
                              token = SecretStr(personal_access_token),  # noqa,
                    path="",
                              )

    pipeline_yaml="""trigger:
- main

steps:
- script: echo hey
- template: some_location/file.yml

a:
  b:
    c:
"""
    yaml_loaders[0](pipeline_yaml, yaml.BaseLoader)
    exit()
    validate(config, pipeline_yaml)


