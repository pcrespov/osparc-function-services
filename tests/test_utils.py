import json
import sys
from pathlib import Path
from typing import Callable

import pytest
import yaml
from osparc_function_services._utils import create_meta
from osparc_function_services.sensitivity_ua_services import (
    sensitivity_ua_linear_regression, sensitivity_ua_test_func)


@pytest.mark.parametrize(
    "service_func", (sensitivity_ua_test_func, sensitivity_ua_linear_regression)
)
def test_create_meta(service_func: Callable, dot_osparc_folder: Path):

    meta = create_meta(service_func, service_version="1.0.0")
    print(json.dumps(meta, indent=1))


    # https://docs.docker.com/engine/reference/commandline/tag/#extended-description
    tag = f"ITISFoundation/{meta['key']}:{meta['version']}"
    assert len(tag) < 128


    dirname = dot_osparc_folder / f"{service_func.__name__}"
    dirname.mkdir(parents=True, exist_ok=True)

    with open(dirname / "metadata.yml", 'wt') as fh:
        yaml.safe_dump(meta, fh, sort_keys=False)
