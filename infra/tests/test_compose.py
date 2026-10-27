import json
import pathlib
import subprocess
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]


def compose_config() -> dict[str, Any]:
    out = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(out)  # type: ignore[no-any-return]


def test_db_image_pinned() -> None:
    assert compose_config()["services"]["db"]["image"] == "postgres:18.6-alpine"


def test_db_has_healthcheck() -> None:
    assert "healthcheck" in compose_config()["services"]["db"]


def test_no_latest_tags() -> None:
    for name, svc in compose_config()["services"].items():
        image = svc["image"]
        assert ":" in image, name
        assert not image.endswith(":latest"), name


def test_redis_image_pinned() -> None:
    assert compose_config()["services"]["redis"]["image"] == "redis:8.8.4-alpine"


def test_redis_eviction_only_volatile() -> None:
    assert "volatile-lru" in compose_config()["services"]["redis"]["command"]
