from typer.testing import CliRunner

from ado_pipeline_helper.cli import cli

runner = CliRunner()

TEST_PIPELINE = "tests/test_pipelines/test_pipeline_1.yml"

def test_preview(pat_env):
    result = runner.invoke(cli, ["preview", TEST_PIPELINE])
    assert result.exit_code == 0, result
    assert "trigger" in result.stdout


def test_validate(pat_env):
    result = runner.invoke(cli, ["validate", TEST_PIPELINE])
    assert result.exit_code == 0, result
    assert "trigger" in result.stdout
