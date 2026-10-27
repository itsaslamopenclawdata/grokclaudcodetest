import pathlib
from typing import Any

import yaml

CI = pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


def _load() -> dict[str, Any]:
    return yaml.safe_load(CI.read_text())  # type: ignore[no-any-return]


def test_backend_job_runs_quality_commands() -> None:
    runs = [s["run"] for s in _load()["jobs"]["backend"]["steps"] if "run" in s]
    expected = [
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run mypy app",
        "uv run pytest -q",
    ]
    positions = [runs.index(cmd) for cmd in expected]
    assert positions == sorted(positions)


def test_services_pinned() -> None:
    services = _load()["jobs"]["backend"]["services"]
    assert services["postgres"]["image"] == "postgres:18.6-alpine"
    assert services["redis"]["image"] == "redis:8.8.4-alpine"


def test_no_secrets_referenced() -> None:
    assert "secrets." not in CI.read_text()
