"""Test configuration.

Puts `src/` and `tests/` on the import path so the suite runs from a source checkout without
installing the package. No test performs network access, writes outside the repository, or
reads any path outside it.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"

for _path in (SRC_DIR, TESTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """The repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def config_dir() -> Path:
    """The repository's shipped `config/` directory."""
    return REPO_ROOT / "config"


@pytest.fixture(scope="session")
def src_dir() -> Path:
    """The `src/` directory."""
    return SRC_DIR
