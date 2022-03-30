import collections.abc
import inspect
from copy import deepcopy
from inspect import Parameter, Signature
from typing import Any, Callable, Dict, Final, TypedDict, get_args, get_origin

from numpy import sign
from pydantic.tools import schema_of

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


def validate_inputs(signature: Signature) -> Dict[str, Any]:
    inputs = {}
    for parameter in signature.parameters.values():
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


def validate_outputs(signature: Signature) -> Dict[str, Any]:
    # TODO: add extra info on outputs
    outputs = {}
    if signature.return_annotation != Signature.empty:
        origin = get_origin(signature.return_annotation)

        if origin and origin is tuple:
            # multiple outputs
            return_args = get_args(signature.return_annotation)
        else:
            # single output
            return_args = (signature.return_annotation, )

        for index, output_parameter in enumerate(return_args, start=1):
            name = f"out_{index}"
            display_name = f"Out{index} {_name_type(output_parameter)}"
            data = {
                "label": display_name,
                "description": "",
                "type": "ref_contentSchema",
                "contentSchema": schema_of(
                    output_parameter,
                    title= display_name,
                ),
            }
            outputs[name] = data
    return outputs

def create_meta(func: Callable, service_version: str) -> MetaDict:

    if inspect.isgeneratorfunction(func):
        raise NotImplementedError(f"Cannot process function iterators as {func}")

    signature = inspect.signature(func)
    inputs = validate_inputs(signature)
    outputs = validate_outputs(signature)

    service_name = f"{func.__module__}.{func.__name__}"

    meta = deepcopy(_TEMPLATE_META)
    meta["name"] = service_name
    meta["key"] = f"simcore/services/comp/ofs-{func.__name__}"
    meta["version"] = service_version
    meta["inputs"] = inputs
    meta["outputs"] = outputs

    return meta
