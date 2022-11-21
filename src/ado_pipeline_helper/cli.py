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
    CliSettings,
    PipeLineSettingsId,
    PipeLineSettingsName,
)

TOKEN_ENV_VAR = "AZURE_DEVOPS_EXT_PAT"

cli = typer.Typer()


def local_pipeline_callback(name: Optional[str]):
    if name is None:
        return name
    pipeline_names = CliSettings.read().get_local_names()
    if name not in pipeline_names:
        raise typer.BadParameter(
            f"Local Pipeline name {name} not found in {DEFAULT_CONFIG_PATH}."
            f"Available: {list(pipeline_names)}"
        )
    return name


pipeline_local_name_option = typer.Option("default", callback=local_pipeline_callback)
token_option = typer.Option(..., envvar=TOKEN_ENV_VAR)


def _get_client(
    path: Optional[Path],
    pipeline_id: Optional[int],
    pipeline_local_name: str,
    token: str,
    organization: str,
    project: str,
    user: str,
) -> Client:
    if organization and project and path:
        settings = CliSettings(organization=organization, project=project, pipelines={})
        if pipeline_id is None:
            settings.pipelines["default"] = PipeLineSettingsName.from_path(path=path)
        else:
            settings.pipelines["default"] = PipeLineSettingsId(
                path=path, name=None, id=pipeline_id
            )
    else:
        settings = CliSettings.read()
    client_settings = ClientSettings.from_cli_settings(
        settings, pipeline_local_name, token=SecretStr(token), user=user
    )
    return Client.from_client_settings(client_settings)


@cli.command()
def preview(
    path: Optional[Path] = typer.Option(None),
    pipeline_id: Optional[int] = typer.Option(None),
    pipeline_local_name: str = pipeline_local_name_option,
    token: str = token_option,
    organization: str = typer.Option(None),
    project: str = typer.Option(None),
    user: str = typer.Option(""),
):
    """Fetch remote pipeline yaml as a single file."""
    client = _get_client(
        path, pipeline_id, pipeline_local_name, token, organization, project, user
    )
    try:
        run = client.preview()
        print(run.final_yaml)
    except AzureDevOpsServiceError as e:
        print(e.message)
        raise typer.Exit(code=1)


@cli.command()
def validate(
    path: Optional[Path] = typer.Option(None),
    pipeline_id: Optional[int] = typer.Option(None),
    pipeline_local_name: str = pipeline_local_name_option,
    token: str = token_option,
    organization: str = typer.Option(None),
    project: str = typer.Option(None),
    user: str = typer.Option(""),
):
    """Check current local pipeline for errors."""
    client = _get_client(
        path, pipeline_id, pipeline_local_name, token, organization, project, user=user
    )
    try:
        run = client.validate()
        print(run.final_yaml)
    except AzureDevOpsServiceError as e:
        print(e.message)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
