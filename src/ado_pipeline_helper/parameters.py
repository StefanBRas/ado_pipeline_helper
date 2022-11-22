"""
https://learn.microsoft.com/en-us/azure/devops/pipelines/process/runtime-parameters?view=azure-devops&tabs=script#parameter-data-types
"""
from typing import Literal, Mapping, Optional, Any, Union

from pydantic import BaseModel


class BaseParameter(BaseModel):
    name: str


class StringParameter(BaseParameter):
    default: Optional[str]
    type: Literal["string"] = "string"


class NumberParameter(BaseParameter):
    default: Optional[int]
    type: Literal["number"] = "number"


class BooleanParameter(BaseParameter):
    default: Optional[bool]
    type: Literal["boolean"] = "boolean"


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


class ParameterList(BaseModel):
    __root__: list[Parameter]

