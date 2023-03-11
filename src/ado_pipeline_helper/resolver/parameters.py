"""
https://learn.microsoft.com/en-us/azure/devops/pipelines/process/runtime-parameters?view=azure-devops&tabs=script#parameter-data-types
"""
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal, Mapping, Optional, Union

from pydantic import BaseModel, Field
from ruamel.yaml.scalarstring import PlainScalarString, ScalarString

PARAMETER_EXPRESSION_REGEX = re.compile(r"\${{\s*parameters\.(\w+)\s*}}")


class BaseParameter(BaseModel):
    name: str
    default: Any

    def get_val(self, input):
        return input if input is not None else self.default


class StringParameter(BaseParameter):
    default: Optional[str]
    type: Literal["string"] = "string"

    def get_val(self, input: Optional[str]) -> str:
        return super().get_val(input)


class NumberParameter(BaseParameter):
    default: Optional[int]  # TODO: can they be float?
    type: Literal["number"] = "number"

    def get_val(self, input: Optional[int]) -> str:
        return str(super().get_val(input))


class BooleanParameter(BaseParameter):
    default: Optional[bool]
    type: Literal["boolean"] = "boolean"

    @staticmethod
    def _val_to_str(val: Optional[bool]) -> Optional[str]:
        if val is None:
            return None
        elif val:
            return "True"
        else:
            return "False"

    def get_val(self, input: Optional[bool]) -> Literal["True", "False"]:
        val = super().get_val(input)
        if type(val) == bool:
            if val:
                return "True"
            else:
                return "False"
        else:
            raise ValueError("Boolean parameter must be true or false")


class ObjectParameter(BaseParameter):
    default: Optional[Any]
    type: Literal["object"] = "object"


class StepParameter(BaseParameter):
    default: Optional[Mapping]
    type: Literal["step"] = "step"


class StepListParameter(BaseParameter):
    default: Optional[list[Mapping]]
    type: Literal["stepList"] = "stepList"


class JobParameter(BaseParameter):
    default: Optional[Mapping]
    type: Literal["job"] = "job"


class JobListParameter(BaseParameter):
    default: Optional[list[Mapping]]
    type: Literal["jobList"] = "jobList"


class DeploymentParameter(BaseParameter):
    default: Optional[Mapping]
    type: Literal["deployment"] = "deployment"


class DeploymentListParameter(BaseParameter):
    default: Optional[list[Mapping]]
    type: Literal["deploymentList"] = "deploymentList"


class StageParameter(BaseParameter):
    default: Optional[Mapping]
    type: Literal["stage"] = "stage"


class StageListParameter(BaseParameter):
    default: Optional[list[Mapping]]
    type: Literal["stageList"] = "stageList"


Parameter = Union[
    StringParameter,
    NumberParameter,
    BooleanParameter,
    ObjectParameter,
    StepParameter,
    StepListParameter,
    JobParameter,
    JobListParameter,
    DeploymentParameter,
    DeploymentListParameter,
    StageParameter,
    StageListParameter,
]


class Parameters(BaseModel):
    __root__: dict[str, Parameter]

    @classmethod
    def from_template(cls, template: dict):
        parameters = template.get("parameters")
        if parameters is None:
            return cls(__root__={})
        else:
            parms = {p["name"]: p for p in parameters}
            return cls(__root__=parms)

    @staticmethod
    def str_has_parameter_expression(input_str: str) -> bool:
        matches = re.findall(PARAMETER_EXPRESSION_REGEX, input_str)
        return bool(matches)

    def sub(self, obj: str, parameter_values: dict):
        """Substitue templated strings with values from parameters"""
        matches = list(re.finditer(PARAMETER_EXPRESSION_REGEX, obj))
        if matches:
            is_single = len(matches[0].group(0)) == len(obj)
            if is_single:
                parameter = self.__root__[matches[0].group(1)]
                val = parameter_values.get(parameter.name)
                return parameter.get_val(val)
            else:
                for match in matches:
                    parameter_name = match.group(1)
                    parameter = self.__root__[parameter_name]
                    val = parameter_values.get(parameter.name)
                    obj = obj.replace(match.group(0), parameter.get_val(val))
                    if isinstance(obj, ScalarString):
                        # Weird edge case, where ADO will drop quotes on a string
                        # if there is a parameter to be substituted into it in
                        # a template. We need to set it to PlainScalarString and
                        # not just str because ruamel will try to preserve
                        # the qutation style when we write back to the CommentedMap (dict).
                        obj = PlainScalarString(str(obj))
                return obj
        else:
            raise Exception("parameter expression not found in input")


class Context(BaseModel):
    """should probably be in another module"""

    parameters: Parameters = Field(default_factory=lambda: Parameters(__root__=dict()))
    parameter_values: dict = Field(default_factory=dict)
    cwd: Path  # For nested templates, i think?

    def merge(self, obj: dict):
        fields = self.__fields__
        for key, val in obj.items():
            if key in fields:
                setattr(self, key, val)
        return self

    def deepcopy(self):
        return deepcopy(self)
