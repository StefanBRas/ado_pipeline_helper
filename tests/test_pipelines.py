from ado_pipeline_helper.client import Client, Run


def test_preview(client: Client):
    preview = client.preview()
    assert isinstance(preview, Run)


def test_validate(client: Client):
    preview = client.preview()
    validated = client.validate()
    assert isinstance(preview, Run), preview
    assert isinstance(validated, Run), (validated, client.load_yaml())
    assert validated.final_yaml == preview.final_yaml
