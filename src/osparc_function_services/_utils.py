import inspect
from copy import deepcopy
from inspect import Parameter, Signature
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


def _replace_value_in_dict(item: Any, original_schema: dict[str, Any]):
    #
    # Taken and adapted from https://github.com/samuelcolvin/pydantic/issues/889#issuecomment-850312496
    # TODO: check https://github.com/gazpachoking/jsonref

    if isinstance(item, list):
        return [_replace_value_in_dict(i, original_schema) for i in item]
    elif isinstance(item, dict):
        if "$ref" in item.keys():
            # Limited to something like "$ref": "#/definitions/Engine"
            definitions = item["$ref"][2:].split("/")
            res = original_schema.copy()
            for definition in definitions:
                res = res[definition]
            return res
        else:
            return {
                key: _replace_value_in_dict(i, original_schema)
                for key, i in item.items()
            }
    else:
        return item


def _resolve_refs(schema: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in str(schema):
        # NOTE: this is a minimal solution that cannot cope e.g. with
        # the most generic $ref with might be URLs. For that we will be using
        # directly jsonschema python package's resolver in the near future.
        # In the meantime we can live with this
        return _replace_value_in_dict(deepcopy(schema), deepcopy(schema.copy()))
    return schema


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
            "contentSchema": _resolve_refs(content_schema),
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
        content_schema = schema_of(return_type, title=display_name)
        data = {
            "label": display_name,
            "description": "",
            "type": "ref_contentSchema",
            "contentSchema": _resolve_refs(content_schema),
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


def define_service(
    version: str,
    outputs: dict[str, Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
    authors: Optional[list] = None,
    contact: Optional[str] = None,
    thumbnail: Optional[str] = None,
):
    # TODO: sync with create_meta
    def _decorator(func: Callable):
        service_name = f"{_PACKAGE_NAME}-{name or func.__name__}"

        meta = deepcopy(_TEMPLATE_META)
        meta["name"] = service_name
        meta["key"] = f"simcore/services/comp/ofs-{func.__name__}"
        meta["version"] = version

        meta["outputs"] = outputs
        func.__meta__ = meta
        return func

    return _decorator
