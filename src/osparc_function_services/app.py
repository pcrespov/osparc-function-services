import json
from optparse import Option
import os
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import (
    Callable,
    Optional,
)
from . import log
from pydantic import BaseModel, BaseSettings, ValidationError, validator
from pydantic.decorator import ValidatedFunction


class Settings(BaseSettings):
    # envs setup by sidecar
    INPUT_FOLDER: Path
    OUTPUT_FOLDER: Path
    LOG_FOLDER: Optional[Path] = None

    SC_BUILD_TARGET: Optional[str] = None
    SC_COMP_SERVICES_SCHEDULED_AS: Optional[str] = None
    SC_USER_ID: Optional[int] = None
    SC_USER_NAME: Optional[str] = None

    SIMCORE_MEMORY_BYTES_LIMIT: Optional[int] = None
    SIMCORE_NANO_CPUS_LIMIT: Optional[int] = None

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
    # TODO: App class? with workflow embedded? split setup + run

    vfunc = ValidatedFunction(function=service_func, config=None)

    # envs and inputs (setup by sidecar)
    try:

        settings = Settings()
        log.info("Settings setup by sidecar %s", settings.json(indent=1))

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
