import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from check_layout import REQUIRED_DIRS, REQUIRED_FILES, missing_paths  # noqa: E402


def test_missing_paths_empty_dir_lists_everything(tmp_path: pathlib.Path) -> None:
    assert missing_paths(tmp_path) == sorted(REQUIRED_DIRS + REQUIRED_FILES)
    assert len(missing_paths(tmp_path)) == 9


def test_missing_paths_complete_dir_is_empty(tmp_path: pathlib.Path) -> None:
    for d in REQUIRED_DIRS:
        (tmp_path / d).mkdir()
    for f in REQUIRED_FILES:
        (tmp_path / f).write_text("")
    assert missing_paths(tmp_path) == []


def test_repo_root_is_complete() -> None:
    assert missing_paths(pathlib.Path(__file__).resolve().parents[1]) == []
