from azure.devops.connection import Connection
from azure.devops.v6_0.pipelines.models import Run
from azure.devops.exceptions import AzureDevOpsServiceError
from msrest.authentication import BasicAuthentication
from ado_pipeline_helper.yaml_loader import YamlResolver, yaml
from ado_pipeline_helper.config import PipelineConfig
from typing import Optional
from pathlib import Path

class PipelineValidationError(Exception):
    pass

class PipelineNotFoundError(Exception):
    pass

class Client:
    def __init__(self, config: PipelineConfig) -> None:
        self._config = config
        self._pipeline_id = config.pipeline_id
        self._pipeline_client = self._get_pipeline_client(config)

    @property
    def pipeline_id(self) -> int:
        if self._pipeline_id is None:
            return self._get_pipeline_id()
        else:
            return self._pipeline_id
        


    def _get_pipeline_client(self, config: PipelineConfig):
        credentials = BasicAuthentication('', config.settings.token.get_secret_value())
        organization_url = f'https://dev.azure.com/{config.settings.organization}'
        connection = Connection(base_url=organization_url, creds=credentials)
        return connection.clients_v6_0.get_pipelines_client()

    def _get_pipeline_id(self) -> int:
        name = yaml.load(Path(self._config.path).read_text())
        project = self._config.settings.project
        pipelines = self._pipeline_client.list_pipelines(project)
        for pipeline in pipelines:
            if pipeline.name == name:
                return pipeline.id
        else:
            raise PipelineNotFoundError(f"No pipeline named {name} was found in {project}")

        

    def load_yaml(self) -> str:
        resolver = YamlResolver(Path(self._config.path))
        return resolver.get_yaml()

    def _call_run_pipeline_endpoint(self, run_parameters: Optional[dict]=None) -> Run | str:
        try:
            return self._pipeline_client.run_pipeline(
                pipeline_id=self.pipeline_id,
                project=self._config.settings.project,
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

