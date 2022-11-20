from pathlib import Path
from typing import Optional
from azure.devops.v6_0.pipelines.models import Run
import typer
from rich import print
from ado_pipeline_helper.client import Client

from ado_pipeline_helper.config import PipelineConfig, Settings

cli = typer.Typer()

def get_client(
    path: Optional[Path] = None,
    pipeline_local_name: Optional[str] =  None,
    organization: Optional[str] =  None,
    project: Optional[str] = None ,
    pipeline_id: Optional[int] = None,
    token: Optional[str] = None,
):
    settings_args = {
        **({'organization': organization} if organization is not None else {}),
        **({'project': project} if project is not None else {}),
        **({'token': token} if token is not None else {}),
    }
    settings = Settings(**settings_args)
    if pipeline_local_name:
        config = PipelineConfig.get_from_pipeline_local_name(settings, pipeline_local_name)
    else:
        config = PipelineConfig(settings=settings, path = path, pipeline_id = pipeline_id)
    client = Client(config)
    return client

@cli.command()
def preview(
    path: Optional[Path] =  typer.Option(None),
    pipeline_local_name: str =  typer.Option(None),
    organization: str =  typer.Option(None),
    project: str = typer.Option(None) ,
    pipeline_id: Optional[int] = typer.Option(None),
    token: Optional[str] = typer.Option(None),
):
    """Fetch remote pipeline yaml as a single file.

    """
    client = get_client(
    path,
    pipeline_local_name,
    organization,
    project,
    pipeline_id,
    token,
    )
    preview = client.preview()
    if isinstance(preview, Run):
        print(preview.final_yaml)
    else:
        print(preview)
        raise typer.Exit(code=1)

@cli.command()
def validate(
    path: Optional[Path] =  typer.Option(None),
    pipeline_local_name: str =  typer.Option(None),
    organization: str =  typer.Option(None),
    project: str = typer.Option(None) ,
    pipeline_id: Optional[int] = typer.Option(None),
    token: Optional[str] = typer.Option(None),
):
    """Check current local pipeline for errors.

    """
    client = get_client(
    path,
    pipeline_local_name,
    organization,
    project,
    pipeline_id,
    token,
    )
    validate = client.validate()
    if isinstance(validate, Run):
        print(validate.final_yaml)
    else:
        print(validate)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
