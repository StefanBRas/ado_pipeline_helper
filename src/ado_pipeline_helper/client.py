from pathlib import Path
from typing import Optional, Union

from azure.devops.connection import Connection
from azure.devops.v6_0.pipelines.models import Run
from msrest.authentication import BasicAuthentication
from pydantic import SecretStr

from ado_pipeline_helper.config import ClientSettings
from ado_pipeline_helper.yaml_loader import YamlResolver


class PipelineValidationError(Exception):
    pass


class PipelineNotFoundError(Exception):
    pass


AdoResponse = Union[Run, str]


class Client:
    def __init__(
        self,
        organization: str,
        project: str,
        token: SecretStr,
        pipeline_path: Path,
        pipeline_id: Optional[int],
        pipeline_name: Optional[str],
        user: str = "",
    ) -> None:
        self._organization = organization
        self._project = project
        self._token = token
        self._pipeline_path = pipeline_path
        self._pipeline_id = pipeline_id
        self._pipeline_name = pipeline_name
        self._user = user
        self._pipeline_client = self._get_pipeline_client()

    @classmethod
    def from_client_settings(cls, settings: ClientSettings):
        return cls(**settings.dict())

    @property
    def pipeline_id(self) -> int:
        if self._pipeline_id is None:
            return self._get_pipeline_id()
        else:
            return self._pipeline_id

    @property
    def pipeline_name(self) -> int:
        if self._pipeline_id is None:
            return self._get_pipeline_id()
        else:
            return self._pipeline_id

    def _get_pipeline_client(self):
        credentials = BasicAuthentication(self._user, self._token.get_secret_value())
        organization_url = f"https://dev.azure.com/{self._organization}"
        connection = Connection(base_url=organization_url, creds=credentials)
        return connection.clients_v6_0.get_pipelines_client()

    def _get_pipeline_id(self) -> int:
        project = self._project
        pipelines = self._pipeline_client.list_pipelines(project)
        for pipeline in pipelines:
            if pipeline.name == self._pipeline_name:
                return pipeline.id
        else:
            raise PipelineNotFoundError(
                f"No pipeline named {self._pipeline_name} was found in {project}"
            )

    def load_yaml(self) -> str:
        resolver = YamlResolver(self._pipeline_path)
        return resolver.get_yaml()

    def _call_run_pipeline_endpoint(self, run_parameters: Optional[dict] = None) -> Run:
        return self._pipeline_client.run_pipeline(
            pipeline_id=self.pipeline_id,
            project=self._project,
            run_parameters=run_parameters if run_parameters is not None else {},
        )

    def validate(self) -> Run:
        run_parameters = {"preview_run": True, "yamlOverride": self.load_yaml()}
        return self._call_run_pipeline_endpoint(run_parameters)

    def run(self) -> Run:
        return self._call_run_pipeline_endpoint()

    def preview(self) -> Run:
        run_parameters = {
            "preview_run": True,
        }
        return self._call_run_pipeline_endpoint(run_parameters)
