import sys
from pathlib import Path

import pytest

CURRENT_DIR = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent


@pytest.fixture(scope="session")
def repo_folder() -> Path:
    assert any(CURRENT_DIR.parent.glob(".git"))
    return CURRENT_DIR.parent


@pytest.fixture(scope="session")
def dot_osparc_folder(repo_folder: Path):
    return repo_folder / ".osparc"
