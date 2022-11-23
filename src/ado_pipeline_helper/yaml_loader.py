from collections.abc import Callable
from dataclasses import dataclass
import re
from io import StringIO
from pathlib import Path
from typing import Any, Literal, Optional, OrderedDict, TypeVar

from pydantic import BaseModel
from ruamel.yaml import YAML

from ado_pipeline_helper.utils import listify, set_if_not_none

class MyYAML(YAML):
    """wrapper so we can dump to a string."""

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

TemplateTypes = Literal["stages", "jobs", "steps", "variables"]


@dataclass()
class TraversalResult:
    has_change: bool
    val: Any


def traverse(obj, mod_func: Callable[..., TraversalResult]=lambda x: TraversalResult(has_change=False, val=x)) :
    mod_func_result = mod_func(obj)
    if mod_func_result.has_change:
        return traverse(mod_func_result.val, mod_func)
    result = mod_func_result.val
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

class YamlResolveError(Exception):
    pass

class YamlResolver:
    def __init__(self, pipeline_path: Path) -> None:
        self.pipeline_path = pipeline_path
        content = self.pipeline_path.read_text()
        self.pipeline: OrderedDict = yaml.load(content)

    def get_yaml(self) -> str:
        def mod_func(obj) -> TraversalResult:
            # is extend template
            if isinstance(obj, dict) and "extends" in obj:
                extend_node = obj['extends']
                relative_path = extend_node["template"]
                if "@" in relative_path:
                    return TraversalResult(False, obj)
                template_path = self.pipeline_path.parent.joinpath(relative_path)
                template_content = template_path.read_text()
                template_dict = yaml.load(template_content)
                new_obj = {'template': relative_path}
                new_obj = set_if_not_none(new_obj, 'parameters', extend_node.get('parameters'))
                if self._is_jobs_template(template_dict):
                    obj['jobs'] = [new_obj]
                elif self._is_steps_template(template_dict):
                    obj['steps'] = [new_obj]
                elif self._is_stages_template(template_dict):
                    obj['stages'] = [new_obj]
                else:
                    raise YamlResolveError('Can only extend from step, job or stage template.')
                del obj['extends']
                print(obj)
                return TraversalResult(True, obj)
            # is a template reference
            if isinstance(obj, dict) and "template" in obj:
                relative_path = obj["template"]
                if "@" in relative_path:
                    return TraversalResult(False, obj)
                template_path = self.pipeline_path.parent.joinpath(relative_path)
                template_content = template_path.read_text()
                template_dict = yaml.load(template_content)
                if self._is_jobs_template(template_dict):
                    return TraversalResult(True, self.handle_jobs_template_dict(template_dict, obj))
                elif self._is_steps_template(template_dict):
                    return TraversalResult(True, self.handle_steps_template_dict(template_dict, obj))
                elif self._is_variables_template(template_dict):
                    return TraversalResult(True, self.handle_variables_template_dict(template_dict, obj))
                elif self._is_stages_template(template_dict):
                    return TraversalResult(True, self.handle_stages_template_dict(template_dict, obj))
                else:
                    raise YamlResolveError('Unsupported template type.')
            return TraversalResult(False, obj)

        yaml_resolved = traverse(self.pipeline, mod_func)
        return str(yaml.dump(yaml_resolved))

    def _handle_parameters(self, template_items, input_parameters:dict, parameters: list[dict]):
        """Substitutes parameters into the template.
        TODO: Breaks on variables that are not strings.
        """
        resolved_parameters = {p['name']: p.get('default') for p in parameters} | input_parameters
        def resolve_steps(obj) -> TraversalResult:
            """replace parameter template syntax with the actual value"""
            if type(obj) == str:
                # TODO: should consider type of parameter
                replaced_string = self.replace_parameters(obj, resolved_parameters)
                if obj == replaced_string:
                    return TraversalResult(False, replaced_string)
                return TraversalResult(True, replaced_string)
            return TraversalResult(False, obj)

        return traverse(template_items, resolve_steps)

    @staticmethod
    def _is_jobs_template(dct: dict):
        return "jobs" in dct.keys()

    @staticmethod
    def _is_steps_template(dct: dict):
        return "steps" in dct.keys()

    @staticmethod
    def _is_variables_template(dct: dict):
        return "variables" in dct.keys()

    @staticmethod
    def _is_stages_template(dct: dict):
        return "stages" in dct.keys()

    def _handle_template(self, dct, template_reference, key: TemplateTypes) -> dict:
        """Resolves jobs template yaml from template reference."""
        template_items = dct.pop(key)
        parameters = dct.get("parameters")
        if parameters:
            template_items = self._handle_parameters(
                template_items, template_reference.get('parameters', {}), parameters
            )
        return template_items

    def handle_jobs_template_dict(self, dct, template_reference) -> dict:
        """Resolves jobs template yaml from template reference."""

        jobs = self._handle_template(dct, template_reference, "jobs")
        return jobs

    def handle_steps_template_dict(self, dct, template_reference) -> dict:
        """Resolves steps template yaml from template reference."""
        steps = self._handle_template(dct, template_reference, "steps")
        return steps

    def handle_stages_template_dict(self, dct, template_reference) -> dict:
        """Resolves stages template yaml from template reference.

        """
        stages = self._handle_template(dct, template_reference, "stages")
        return stages

    def handle_variables_template_dict(self, dct, template_reference) -> list:
        """Resolves variables template yaml from template reference.

        Assumes that variables are either a short-form dict with
        name-value or the list form of name-value-type-default dicts.

        Maybe this is not true and they can be mixed.

        """
        variables = self._handle_template(dct, template_reference, "variables")
        if isinstance(variables, dict):
            return [{"name": key, "value": value} for key, value in variables.items()]
        return variables

    @staticmethod
    def replace_parameters(input: str, parameters: Optional[dict] = None):
        if parameters is None:
            return input
        for p_name, p_value in parameters.items():
            pattern = r"\${{ parameters\." + p_name + r" }}"
            input = re.sub(pattern, p_value, input)
        return input
