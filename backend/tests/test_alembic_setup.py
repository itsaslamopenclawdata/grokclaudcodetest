import pathlib

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util.exc import CommandError


def test_script_directory_loads() -> None:
    script = ScriptDirectory.from_config(Config("alembic.ini"))
    assert script.get_heads() == ["0002"]


def test_env_targets_base_metadata() -> None:
    assert "target_metadata = Base.metadata" in pathlib.Path("alembic/env.py").read_text()


def test_upgrade_unknown_revision_fails() -> None:
    cfg = Config("alembic.ini")
    with pytest.raises(CommandError):
        command.upgrade(cfg, "doesnotexist")
