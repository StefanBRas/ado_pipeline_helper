from pathlib import Path
from typing import Optional

import typer
from azure.devops.exceptions import AzureDevOpsServiceError
from pydantic import SecretStr
from rich import print

from ado_pipeline_helper.client import Client
from ado_pipeline_helper.config import (
    DEFAULT_CONFIG_PATH,
    ClientSettings,
    CliSettingsFile,
)

TOKEN_ENV_VAR = "AZURE_DEVOPS_EXT_PAT"

cli = typer.Typer()

token_option = typer.Option(..., envvar=TOKEN_ENV_VAR)


def _get_client(
    path: Path,
    pipeline_id: Optional[int],
    token: str,
    organization: Optional[str],
    project: Optional[str],
    user: str,
) -> Client:
    settings_from_config_file = CliSettingsFile.read(config_path=DEFAULT_CONFIG_PATH)
    pipeline_settings_from_file = settings_from_config_file.pipelines.get(path)
    overrides = None
    if pipeline_settings_from_file is not None:
        pipeline_id = pipeline_id or pipeline_settings_from_file.id
        overrides = (
            pipeline_settings_from_file.overrides or settings_from_config_file.overrides
        )
    client_settings = ClientSettings.parse_obj(
        {
            "organization": organization or settings_from_config_file.organization,
            "project": project or settings_from_config_file.project,
            "pipeline_id": pipeline_id,
            "pipeline_path": path,
            "token": SecretStr(token),
            "user": user,
            "overrides": overrides or {},
        }
    )
    return Client.from_client_settings(client_settings)


@cli.command()
def preview(
    path: Path = typer.Argument(None),
    pipeline_id: Optional[int] = typer.Option(None),
    token: str = token_option,
    organization: str = typer.Option(None),
    project: str = typer.Option(None),
    user: str = typer.Option(""),
):
    """Fetch remote pipeline yaml as a single file."""
    client = _get_client(path, pipeline_id, token, organization, project, user)
    try:
        run = client.preview()
        print(run.final_yaml)
    except AzureDevOpsServiceError as e:
        print(e.message)
        raise typer.Exit(code=1)


@cli.command()
def validate(
    path: Path = typer.Argument(...),
    pipeline_id: Optional[int] = typer.Option(None),
    token: str = token_option,
    organization: str = typer.Option(None),
    project: str = typer.Option(None),
    user: str = typer.Option(""),
):
    """Check current local pipeline for errors."""
    client = _get_client(path, pipeline_id, token, organization, project, user=user)
    try:
        run = client.validate()
        print(run.final_yaml)
    except AzureDevOpsServiceError as e:
        print(e.message)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
