from ado_pipeline_helper.client import Client, Run


def test_preview(client: Client):
    preview = client.preview()
    assert isinstance(preview, Run)


def test_validate(client: Client):
    preview = client.preview()
    validated = client.validate()
    with open("tmp.yml", "w") as f:
        f.write(client.load_yaml())
    assert isinstance(preview, Run)
    assert isinstance(validated, Run)
    assert validated.final_yaml == preview.final_yaml
