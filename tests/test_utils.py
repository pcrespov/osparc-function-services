import json
import os
from pathlib import Path
from typing import Callable

import pytest
import yaml
from osparc_function_services._utils import create_meta
from osparc_function_services.sensitivity_ua_services import (
    sensitivity_ua_linear_regression,
    sensitivity_ua_test_func,
)
from pydantic import BaseModel
from pydantic.decorator import ValidatedFunction
from pytest import MonkeyPatch


@pytest.fixture
def sidecar_setup_env(monkeypatch: MonkeyPatch, tmp_path: Path, service_func: Callable):

    input_dir = tmp_path / "inputs"
    input_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("INPUT_FOLDER", f"{input_dir}")

    output_dir = tmp_path / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("OUTPUT_FOLDER", f"{output_dir}")

    input_file = input_dir / "inputs.json"

    if service_func.__name__ == "sensitivity_ua_test_func":
        input_file.write_text(json.dumps({"x": [1, 2, 3, 4]}))
    else:
        raise NotImplementedError(f"no data for {service_func.__name__} ")


@pytest.mark.parametrize("service_func", (sensitivity_ua_test_func,))
def test_setup_execution_teardown(service_func: Callable, sidecar_setup_env: None):
    input_dir = Path(os.environ["INPUT_FOLDER"])
    output_dir = Path(os.environ["OUTPUT_FOLDER"])

    vfunc = ValidatedFunction(function=service_func, config=None)

    inputs: BaseModel = vfunc.model.parse_file(input_dir / "inputs.json")

    returned_values = vfunc.execute(inputs)

    # TODO: verify outputs match with expected?
    # TODO: sync name
    if not isinstance(returned_values, tuple):
        returned_values = (returned_values,)

    outputs = {
        f"out_{index}": value for index, value in enumerate(returned_values, start=1)
    }
    (output_dir / "output.json").write_text(json.dumps(outputs))


@pytest.mark.parametrize(
    "service_func", (sensitivity_ua_test_func, sensitivity_ua_linear_regression)
)
def test_create_meta(service_func: Callable, dot_osparc_folder: Path):
    """tests and produces ./osparc/*/metadata.yml files for every function-service"""

    meta = create_meta(service_func, service_version="1.0.0")
    print(json.dumps(meta, indent=1))

    # https://docs.docker.com/engine/reference/commandline/tag/#extended-description
    tag = f"ITISFoundation/{meta['key']}:{meta['version']}"
    assert len(tag) < 128

    dirname = dot_osparc_folder / f"{service_func.__name__}"
    dirname.mkdir(parents=True, exist_ok=True)

    with open(dirname / "metadata.yml", "wt") as fh:
        yaml.safe_dump(meta, fh, sort_keys=False)
