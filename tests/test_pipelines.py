from ado_pipeline_helper import Client, Run
from ado_pipeline_helper.yaml_loader import yaml

def test_preview(client: Client):
    preview = client.preview()
    assert isinstance(preview, Run)


def test_validate(client: Client):
    preview = client.preview()
    validated = client.validate()

    assert isinstance(preview, Run)
    assert isinstance(validated, Run), client.load_yaml()
    print(client.load_yaml())
    assert validated.final_yaml == preview.final_yaml
    assert yaml.load(validated.final_yaml) == yaml.load(preview.final_yaml)
    assert False

