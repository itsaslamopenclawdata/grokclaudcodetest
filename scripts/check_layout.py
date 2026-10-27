"""Verify the planned repository layout exists."""

import pathlib

REQUIRED_DIRS: tuple[str, ...] = ("backend", "frontend", "infra", "loadtest", "scripts", "docs")
REQUIRED_FILES: tuple[str, ...] = (".gitignore", ".editorconfig", ".env.example")


def missing_paths(root: pathlib.Path) -> list[str]:
    missing = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
    missing += [f for f in REQUIRED_FILES if not (root / f).is_file()]
    return sorted(missing)


def main() -> int:
    missing = missing_paths(pathlib.Path(__file__).resolve().parents[1])
    for path in missing:
        print(path)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
