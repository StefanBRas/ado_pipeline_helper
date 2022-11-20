from pathlib import Path
import contextlib
from typing import OrderedDict
from ruamel.yaml import YAML, StringIO

class MyYAML(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()

yaml = MyYAML()
unordered_yaml=MyYAML(typ='safe')

def is_jobs_template(dct: dict):
    return "jobs" in dct.keys()

def is_steps_template(dct: dict):
    return "steps" in dct.keys()

class YamlResolver:
    def __init__(self, pipeline_path: Path) -> None:
        self.pipeline_path = pipeline_path
        content = self.pipeline_path.read_text()
        self.pipeline: OrderedDict = yaml.load(content)

    def get_yaml(self) -> str:
        for key, val in self.pipeline.items():
            if isinstance(val, dict):
                self.pipeline[key] = self.handle_dict(val)
            elif isinstance(val, list):
                self.pipeline[key] = self.handle_list(val)
        return str(yaml.dump(self.pipeline))


    def handle_dict(self, dct: dict):
        for key,val in list(dct.items()):
            if key == "template":
                template_path = self.pipeline_path.parent.joinpath(val)
                template_content = template_path.read_text()
                template_dict = yaml.load(template_content)
                if is_jobs_template(template_dict):
                    return self.handle_jobs_template_dict(template_dict)
                elif is_steps_template(template_dict):
                    return self.handle_steps_template_dict(template_dict)
            if isinstance(val, dict):
                dct[key] = self.handle_dict(val)
            elif isinstance(val, list):
                dct[key] = self.handle_list(val)
        return dct

    def handle_list(self, lst: list):
        new_list = []
        for val in lst:
            result = []
            if isinstance(val, dict):
                result = self.handle_dict(val)
            elif isinstance(val, list):
                result = self.handle_list(val)
            else:
                new_list.append(val)
            if result:
                if isinstance(result, list):
                    new_list.extend(result)
                else:
                    new_list.append(result)
        return new_list

    def handle_jobs_template_dict(self, dct) -> dict:
        return dct['jobs']

    def handle_steps_template_dict(self, dct) -> dict:
        return dct['steps']

