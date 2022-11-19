import yaml


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
