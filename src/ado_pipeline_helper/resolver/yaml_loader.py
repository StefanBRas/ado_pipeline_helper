from collections.abc import Callable
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Literal, OrderedDict

from ruamel.yaml import YAML

from ado_pipeline_helper.resolver.expression import ExpressionResolver
from ado_pipeline_helper.resolver.parameters import Context, Parameters
from ado_pipeline_helper.utils import listify, set_if_not_none


class YamlStrDumper(YAML):
    """wrapper so we can dump to a string."""

    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


yaml = YamlStrDumper()
yaml.preserve_quotes = True  # type:ignore
unordered_yaml = YamlStrDumper(typ="safe")  # sic

TemplateTypes = Literal["stages", "jobs", "steps", "variables"]


@dataclass()
class TraversalResult:
    has_change: bool
    val: Any
    context: Context


def traverse(
    obj,
    mod_func: Callable[..., TraversalResult],
    context: Context,
):
    mod_func_result = mod_func(obj, context)
    if mod_func_result.has_change:
        return traverse(mod_func_result.val, mod_func, mod_func_result.context)
    result = mod_func_result.val
    if isinstance(obj, list):
        new_list = []
        for val in obj:
            result = traverse(val, mod_func, mod_func_result.context)
            new_list.extend(listify(result))
        return new_list  # type:ignore
    if isinstance(obj, dict):
        for key, val in list(obj.items()):
            result = traverse(val, mod_func, mod_func_result.context)
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
        def mod_func(obj, context: Context) -> TraversalResult:
            # is extend template
            if isinstance(obj, dict) and "extends" in obj:
                extend_node = obj["extends"]
                relative_path = extend_node["template"]
                if "@" in relative_path:
                    return TraversalResult(False, obj, context)
                template_path = context.cwd.parent.joinpath(relative_path)
                template_content = template_path.read_text()
                template_dict = yaml.load(template_content)
                new_obj = {"template": relative_path}
                new_obj = set_if_not_none(
                    new_obj, "parameters", extend_node.get("parameters")
                )
                if self._is_jobs_template(template_dict):
                    obj["jobs"] = [new_obj]
                elif self._is_steps_template(template_dict):
                    obj["steps"] = [new_obj]
                elif self._is_stages_template(template_dict):
                    obj["stages"] = [new_obj]
                else:
                    raise YamlResolveError(
                        "Can only extend from step, job or stage template."
                    )
                del obj["extends"]
                return TraversalResult(True, obj, context)
            # is a template reference
            if isinstance(obj, dict) and "template" in obj:
                relative_path = obj["template"]
                if "@" in relative_path:
                    return TraversalResult(False, obj, context)
                template_path = context.cwd.parent.joinpath(relative_path)
                template_content = template_path.read_text()
                template_dict = yaml.load(template_content)
                parameters = Parameters.from_template(template_dict)
                if self._is_jobs_template(template_dict):
                    template_resolved = self.handle_jobs_template_dict(
                        template_dict, obj, context
                    )
                elif self._is_steps_template(template_dict):
                    template_resolved = self.handle_steps_template_dict(
                        template_dict, obj, context
                    )
                elif self._is_variables_template(template_dict):
                    template_resolved = self.handle_variables_template_dict(
                        template_dict, obj, context
                    )
                elif self._is_stages_template(template_dict):
                    template_resolved = self.handle_stages_template_dict(
                        template_dict, obj, context
                    )
                else:
                    raise YamlResolveError("Unsupported template type.")
                new_context = Context(
                    cwd=template_path,
                    parameters=parameters,
                    parameter_values=obj.get("parameters", {}),
                )
                return TraversalResult(True, template_resolved, new_context)
            # Expression
            if isinstance(obj, str) and ExpressionResolver.find_expression_in_string(
                obj
            ):
                # TODO: handle this better when we dont resolve to a string
                expression_resolver = ExpressionResolver(context=context)
                expression: str = ExpressionResolver.find_expression_in_string(obj)  # type: ignore
                new_obj = expression_resolver.evaluate(expression)["val"]
                # Yeah, this is not good.
                # The issue is that new_obj might be some weird
                # ruamel.Doublescalarstring whatever
                if type(new_obj) in [str, bool, int, float] or isinstance(new_obj, str):
                    new_obj = obj.replace(expression, str(new_obj))
                    print(new_obj)
                return TraversalResult(True, new_obj, context)
            return TraversalResult(False, obj, context)

        initial_context = Context(cwd=self.pipeline_path)
        yaml_resolved = traverse(self.pipeline, mod_func, context=initial_context)
        return str(yaml.dump(yaml_resolved))

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

    def _handle_template(
        self, dct, template_reference, key: TemplateTypes, context: Context
    ) -> dict:
        """Resolves jobs template yaml from template reference."""
        template_items = dct.pop(key)
        return template_items

    def handle_jobs_template_dict(self, dct, template_reference, context) -> dict:
        """Resolves jobs template yaml from template reference."""

        jobs = self._handle_template(dct, template_reference, "jobs", context)
        return jobs

    def handle_steps_template_dict(self, dct, template_reference, context) -> dict:
        """Resolves steps template yaml from template reference."""
        steps = self._handle_template(dct, template_reference, "steps", context)
        return steps

    def handle_stages_template_dict(self, dct, template_reference, context) -> dict:
        """Resolves stages template yaml from template reference."""
        stages = self._handle_template(dct, template_reference, "stages", context)
        return stages

    def handle_variables_template_dict(self, dct, template_reference, context) -> list:
        """Resolves variables template yaml from template reference.

        Assumes that variables are either a short-form dict with
        name-value or the list form of name-value-type-default dicts.

        Maybe this is not true and they can be mixed.

        """
        variables = self._handle_template(dct, template_reference, "variables", context)
        if isinstance(variables, dict):
            return [{"name": key, "value": value} for key, value in variables.items()]
        return variables