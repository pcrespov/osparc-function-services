import inspect
import json
import logging
import os
from copy import deepcopy
from inspect import Parameter, Signature
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Mapping,
    Optional,
    Tuple,
    get_args,
    get_origin,
)

from pydantic import BaseModel, BaseSettings, ValidationError, validator
from pydantic.decorator import ValidatedFunction
from pydantic.tools import schema_of

# FIXME: name and key seem to be the same??!
_PACKAGE_NAME: Final = "ofs"  # __name__.split(".")[0]
_TEMPLATE_META: Final = {
    "name": "TO_BE_DEFINED",
    "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Test.svg/315px-Test.svg.png",
    "description": "",
    "key": "simcore/services/comp/TO_BE_DEFINED",
    "version": "TO_BE_DEFINED",
    "integration-version": "1.0.0",
    "type": "computational",
    "authors": [
        {
            "name": "Pedro Crespo-Valero",
            "email": "crespo@itis.swiss",
            "affiliation": "IT'IS Foundation",
        },
    ],
    "contact": "crespo@itis.swiss",
    "inputs": {},
    "outputs": {},
}


# TODO: class MetaDict(TypedDict):
#    name: str
#    thumbnail: str
#    description: str

MetaDict = Dict[str, Any]


log = logging.getLogger(_PACKAGE_NAME)


def _name_type(parameter_annotation):
    try:
        if issubclass(parameter_annotation, float):
            name = "number"
        elif issubclass(parameter_annotation, int):
            name = "integer"
        elif issubclass(parameter_annotation, str):
            name = "string"
        else:
            name = f"{parameter_annotation}".replace("typing.", "")
    except TypeError:
        name = f"{parameter_annotation}".replace("typing.", "")

    return name


def validate_inputs(parameters: Mapping[str, Parameter]) -> Dict[str, Any]:
    inputs = {}
    for parameter in parameters.values():
        # should only allow keyword argument
        assert parameter.kind == parameter.KEYWORD_ONLY
        assert parameter.annotation != Parameter.empty

        # build each input
        description = getattr(
            parameter.annotation,
            "description",
            parameter.name.replace("_", " ").capitalize(),
        )

        # FIXME: files are represented differently!

        content_schema = schema_of(
            parameter.annotation,
            title=parameter.name.capitalize(),
        )

        data = {
            "label": parameter.name,
            "description": description,
            "type": "ref_contentSchema",
            "contentSchema": content_schema,
        }

        if parameter.default != Parameter.empty:
            # TODO: what if partial-field defaults?
            data["defaultValue"] = parameter.default

        inputs[parameter.name] = data
    return inputs


def _as_args_tuple(return_annotation: Any) -> Tuple:
    if return_annotation == Signature.empty:
        return tuple()

    origin = get_origin(return_annotation)

    if origin and origin is tuple:
        # multiple outputs
        return_args_types = get_args(return_annotation)
    else:
        # single output
        return_args_types = (return_annotation,)
    return return_args_types


def validate_outputs(return_annotation: Any) -> Dict[str, Any]:
    # TODO: add extra info on outputs?
    outputs = {}

    return_args_types = _as_args_tuple(return_annotation)
    for index, return_type in enumerate(return_args_types, start=1):
        name = f"out_{index}"

        display_name = f"Out{index} {_name_type(return_type)}"
        data = {
            "label": display_name,
            "description": "",
            "type": "ref_contentSchema",
            "contentSchema": schema_of(
                return_type,
                title=display_name,
            ),
        }
        outputs[name] = data
    return outputs


def create_meta(func: Callable, service_version: str) -> MetaDict:

    if inspect.isgeneratorfunction(func):
        raise NotImplementedError(f"Cannot process function iterators as {func}")

    signature = inspect.signature(func)
    inputs = validate_inputs(signature.parameters)
    outputs = validate_outputs(signature.return_annotation)

    service_name = f"{_PACKAGE_NAME}-{func.__name__}"

    meta = deepcopy(_TEMPLATE_META)
    meta["name"] = service_name
    meta["key"] = f"simcore/services/comp/ofs-{func.__name__}"
    meta["version"] = service_version
    meta["inputs"] = inputs
    meta["outputs"] = outputs

    return meta


class Settings(BaseSettings):
    # envs setup by sidecar
    INPUT_FOLDER: Path
    OUTPUT_FOLDER: Path
    LOG_FOLDER: Path

    SC_COMP_SERVICES_SCHEDULED_AS: Optional[str] = None
    SIMCORE_NANO_CPUS_LIMIT: Optional[int] = None
    SIMCORE_MEMORY_BYTES_LIMIT: Optional[int] = None

    @validator("INPUT_FOLDER", "OUTPUT_FOLDER", "LOG_FOLDER")
    def check_dir_existance(cls, v):
        if not v.exists():
            raise ValueError(
                f"Folder {v} does not exists."
                "Expected predefined and created by sidecar"
            )
        return v

    @validator("INPUT_FOLDER")
    def check_input_dir(cls, v: Path):
        f = v / "inputs.json"
        if not f.exists():
            raise ValueError(
                f"File {f} does not exists."
                "Expected predefined and created by sidecar"
            )
        return v

    @validator("OUTPUT_FOLDER")
    def check_output_dir(cls, v: Path):
        if not os.access(v, os.W_OK):
            raise ValueError(f"Do not have write access to {v}: {v.stat()}")
        return v

    @property
    def input_file(self) -> Path:
        return self.INPUT_FOLDER / "inputs.json"

    @property
    def output_file(self) -> Path:
        return self.OUTPUT_FOLDER / "outputs.json"


def run_as_service(service_func: Callable):

    vfunc = ValidatedFunction(function=service_func, config=None)

    # envs and inputs (setup by sidecar)
    try:
        settings = Settings()
        log.info("Settings setup by sidecar", settings.json(indent=1))

        inputs: BaseModel = vfunc.model.parse_file(settings.input_file)

    except JSONDecodeError as err:
        raise ValueError(
            f"Invalid input file ({settings.input_file}) json format: {err}"
        ) from err

    except ValidationError as err:
        raise ValueError(f"Invalid inputs for {service_func.__name__}: {err}") from err

    # executes
    returned_values = vfunc.execute(inputs)

    # outputs (expected by sidecar)
    # TODO: verify outputs match with expected?
    # TODO: sync name
    if not isinstance(returned_values, tuple):
        returned_values = (returned_values,)

    outputs = {
        f"out_{index}": value for index, value in enumerate(returned_values, start=1)
    }
    settings.output_file.write_text(json.dumps(outputs))
