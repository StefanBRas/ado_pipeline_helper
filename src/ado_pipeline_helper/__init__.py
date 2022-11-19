from pydantic import BaseModel, SecretStr
from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from msrest.authentication import BasicAuthentication
import yaml
from yaml.constructor import ConstructorError


class Config(BaseModel):
    organization: str
    project: str
    pipeline_id: int
    token: SecretStr

def validate(config: Config, yaml_override: str):
    credentials = BasicAuthentication('', config.token.get_secret_value())
    organization_url = f'https://dev.azure.com/{config.organization}'
    connection = Connection(base_url=organization_url, creds=credentials)
    pipeline_client = connection.clients_v6_0.get_pipelines_client()
    try:
        return pipeline_client.run_pipeline(
            pipeline_id=config.pipeline_id,
            project=config.project,
            run_parameters={
                "preview_run": True,
                "yamlOverride": yaml_override 
            }
        )
    except AzureDevOpsServiceError as e:
        print(e.message)


def template_loader(loader, node, deep=False):
    """if something is a template, resolve it.

    """
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key == 'template':
            value = loader.construct_object(value_node, deep=deep)
            with open(value) as template_file:
                template = yaml.load(template_file, Loader=yaml.BaseLoader)
    return loader.construct_mapping(node, deep)

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, template_loader, yaml.BaseLoader)

yaml_loaders = [yaml.load, yaml.safe_load]



if __name__ == "__main__":
    personal_access_token = "rvg2pydxvliujhijmcjpmb5kh7sicjefq6sby5iav7ncwwxu5xdq"
    config = Config(organization="sbras", project="pypeline",
                              pipeline_id=1,
                              token = SecretStr(personal_access_token),  # noqa
                              )

    pipeline_yaml="""trigger:
- main

steps:
- script: echo hey
- template: some_location/file.yml

a:
  b:
    c:
"""
    yaml_loaders[0](pipeline_yaml, yaml.BaseLoader)
    exit()
    validate(config, pipeline_yaml)


