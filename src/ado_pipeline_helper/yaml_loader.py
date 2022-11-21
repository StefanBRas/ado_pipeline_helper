import re
from io import StringIO
from pathlib import Path
from typing import Literal, Optional, OrderedDict, TypeVar

from pydantic import BaseModel
from ruamel.yaml import YAML

from ado_pipeline_helper.utils import listify


class Parameter(BaseModel):
    name: str
    default: Optional[str]
    type: Literal["boolean", "string"]


class Parameters(BaseModel):
    __root__: Parameter

    @classmethod
    def from_parameter_dict(cls):
        """
        TODO finish this

        """
        pass


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
yaml.preserve_quotes = True  # type:ignore
unordered_yaml = MyYAML(typ="safe")


def is_jobs_template(dct: dict):
    return "jobs" in dct.keys()


def is_steps_template(dct: dict):
    return "steps" in dct.keys()

def is_variables_template(dct: dict):
    return "variables" in dct.keys()


def id_func(obj):
    return obj


T = TypeVar("T")


def traverse(obj: T, mod_func=id_func) -> T:
    if (result := mod_func(obj)) is not None:
        return result
    if isinstance(obj, list):
        new_list = []
        for val in obj:
            result = traverse(val, mod_func)
            new_list.extend(listify(result))
        return new_list  # type:ignore
    if isinstance(obj, dict):
        for key, val in list(obj.items()):
            result = traverse(val, mod_func)
            obj[key] = result
        return obj
    return obj


class YamlResolver:
    def __init__(self, pipeline_path: Path) -> None:
        self.pipeline_path = pipeline_path
        content = self.pipeline_path.read_text()
        self.pipeline: OrderedDict = yaml.load(content)

    def get_yaml(self) -> str:
        def mod_func(obj):
            if isinstance(obj, dict) and "template" in list(obj.keys()):
                if "@" in obj['template']:
                    return None
                relative_path = obj["template"]
                template_path = self.pipeline_path.parent.joinpath(relative_path)
                template_content = template_path.read_text()
                template_dict = yaml.load(template_content)
                if is_jobs_template(template_dict):
                    return self.handle_jobs_template_dict(template_dict, obj)
                elif is_steps_template(template_dict):
                    return self.handle_steps_template_dict(template_dict, obj)
                elif is_variables_template(template_dict):
                    return self.handle_variables_template_dict(template_dict, obj)
                return template_dict
            return None

        yaml_resolved = traverse(self.pipeline, mod_func)
        return str(yaml.dump(yaml_resolved))

    def handle_jobs_template_dict(self, dct, template_reference) -> dict:
        """Resolves jobs template yaml from template reference.

        TODO: Breaks on everything that is not a string.

        TODO: getting the parameters should be split into it's own function
        """
        jobs = dct.pop("jobs")
        parameters = dct.get("parameters")
        if parameters:
            parameter_values = template_reference.get("parameters", {})
            for parameter in parameters:
                default = parameter.get("default")
                if default is not None:
                    parameter_values.setdefault(parameter["name"], default)

            def resolve_steps(obj):
                if type(obj) == str:
                    # TODO: should consider type of parameter
                    return self.replace_parameters(obj, parameter_values)
                return None

            jobs = traverse(jobs, resolve_steps)
        return jobs

    def handle_steps_template_dict(self, dct, template_reference) -> dict:
        """Resolves steps template yaml from template reference.

        TODO: Breaks on everything that is not a string.
        """
        steps = dct.pop("steps")
        parameters = dct.get("parameters")
        if parameters:
            parameter_values = template_reference.get("parameters", {})
            for parameter in parameters:
                default = parameter.get("default")
                if default is not None:
                    parameter_values.setdefault(parameter["name"], default)

            def resolve_steps(obj):
                if type(obj) == str:
                    # TODO: should consider type of parameter
                    return self.replace_parameters(obj, parameter_values)
                return None

            steps = traverse(steps, resolve_steps)
        return steps

    def handle_variables_template_dict(self, dct, template_reference) -> list:
        """Resolves variables template yaml from template reference.

        TODO: Breaks on everything that is not a string.
        """
        variables = dct.pop("variables")
        parameters = dct.get("parameters")
        if parameters:
            parameter_values = template_reference.get("parameters", {})
            for parameter in parameters:
                default = parameter.get("default")
                if default is not None:
                    parameter_values.setdefault(parameter["name"], default)

            def resolve_variables(obj):
                if type(obj) == str:
                    # TODO: should consider type of parameter
                    return self.replace_parameters(obj, parameter_values)
                return None

            variables = traverse(variables, resolve_variables)
        if isinstance(variables, dict):
            return [
                {"name": key, "value": value} for key, value in variables.items()
            ]
        return variables

    @staticmethod
    def replace_parameters(input: str, parameters: Optional[dict] = None):
        if parameters is None:
            return input
        for p_name, p_value in parameters.items():
            pattern = r"\${{ parameters\." + p_name + r" }}"
            input = re.sub(pattern, p_value, input)
        return input
