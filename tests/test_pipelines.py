from ado_pipeline_helper import Client, Run
from ado_pipeline_helper.yaml_loader import unordered_yaml as yaml

def test_preview(client: Client):
    preview = client.preview()
    assert isinstance(preview, Run)


def test_validate(client: Client):
    preview = client.preview()
    validated = client.validate()
    assert isinstance(preview, Run)
    assert isinstance(validated, Run), client.load_yaml()
    assert yaml.load(validated.final_yaml)['stages'][0]['jobs']== yaml.load(preview.final_yaml)['stages'][0]['jobs']
    assert yaml.load(validated.final_yaml)['stages'][0]== yaml.load(preview.final_yaml)['stages'][0]
    assert yaml.load(validated.final_yaml)['stages']== yaml.load(preview.final_yaml)['stages']
    assert yaml.load(validated.final_yaml) == yaml.load(preview.final_yaml)
    assert False

