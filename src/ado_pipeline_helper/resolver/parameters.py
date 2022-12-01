"""
https://learn.microsoft.com/en-us/azure/devops/pipelines/process/runtime-parameters?view=azure-devops&tabs=script#parameter-data-types
"""
import re
from typing import Any, Literal, Mapping, Optional, Union

from pydantic import BaseModel, Field
from pathlib import Path


class BaseParameter(BaseModel):
    name: str
    default: Any

    def sub(self, input, obj):
        return input if input is not None else self.default

    def _strsub(self, input: Optional[str], obj: str, default: Optional[str]):
        replacement = input if input is not None else default
        if not replacement:
            raise ValueError(f"Value missing and no default for {self.name}")
        pattern = r"\${{ parameters\." + self.name + r" }}"
        input = re.sub(pattern, replacement, obj)
        return input


class StringParameter(BaseParameter):
    default: Optional[str]
    type: Literal["string"] = "string"

    def sub(self, input: Optional[str], obj: str):
        return self._strsub(input, obj, self.default)


class NumberParameter(BaseParameter):
    default: Optional[int]
    type: Literal["number"] = "number"

    def sub(self, input: Optional[int], obj):
        return self._strsub(
            str(input) if input is not None else None,
            obj,
            str(self.default) if self.default is not None else None,
        )


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

    def sub(self, input: Optional[bool], obj):
        return self._strsub(
            self._val_to_str(input),
            obj,
            self._val_to_str(self.default),
        )


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

    def find_parameter_in_string(self, input_str) -> Optional[Parameter]:
        matches = re.findall(r"\${{ parameters\.(\w+)", input_str)
        if matches:
            return self.__root__[matches[0]]
        else:
            return None


class Context(BaseModel):
    parameters: Parameters = Field(default_factory= lambda: Parameters(__root__=dict()))
    parameter_values: dict = Field(default_factory=dict)
    variables: dict  = Field(default_factory=dict)
    cwd: Path = Path('.')

    def merge(self, obj: dict):
        fields = self.__fields__
        for key, val in obj.items():
            if key in fields:
                setattr(self, key, val)
        return self


