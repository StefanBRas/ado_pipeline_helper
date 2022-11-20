from typer.testing import CliRunner

from ado_pipeline_helper.cli import cli

runner = CliRunner()


def test_preview(pat_env):
    result = runner.invoke(cli, ["preview"])
    assert result.exit_code == 0
    assert "trigger" in result.stdout

def test_validate(pat_env):
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 0
    assert "trigger" in result.stdout

