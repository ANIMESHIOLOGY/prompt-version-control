import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from promptvc.cli import app
from tests.fixtures.sample_prompts import CLASSIFIER_V1, SUMMARIZER_V1, SUMMARIZER_V2

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run every test in an isolated temp directory with a fresh .promptvc store."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def test_init_creates_store(isolated_dir: Path) -> None:
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (isolated_dir / ".promptvc" / "store.db").exists()
    assert (isolated_dir / ".promptvc" / "config.toml").exists()
    assert (isolated_dir / ".promptvc" / ".staged").is_dir()


def test_init_already_initialized(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Already initialized" in result.stdout


# ---------------------------------------------------------------------------
# add + commit
# ---------------------------------------------------------------------------


def _stage_and_commit(name: str, content: str, message: str = "initial") -> None:
    """Helper: write content via stdin and commit."""
    tmp = Path(os.getcwd()) / f"_tmp_{name}.txt"
    tmp.write_text(content, encoding="utf-8")
    runner.invoke(app, ["add", name, "--file", str(tmp)])
    runner.invoke(app, ["commit", name, "-m", message])
    tmp.unlink(missing_ok=True)


def test_add_from_file(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    f = isolated_dir / "prompt.txt"
    f.write_text(SUMMARIZER_V1, encoding="utf-8")
    result = runner.invoke(app, ["add", "summarizer", "--file", str(f)])
    assert result.exit_code == 0
    staged = isolated_dir / ".promptvc" / ".staged" / "summarizer.txt"
    assert staged.exists()
    assert staged.read_text(encoding="utf-8") == SUMMARIZER_V1


def test_commit_creates_version(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    result = runner.invoke(app, ["log", "summarizer"])
    assert result.exit_code == 0
    assert "v1" in result.stdout


def test_commit_duplicate_content_skipped(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    _stage_and_commit("summarizer", SUMMARIZER_V1, "duplicate attempt")
    result = runner.invoke(app, ["log", "summarizer"])
    assert "v2" not in result.stdout


def test_commit_increments_version(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "v1")
    _stage_and_commit("summarizer", SUMMARIZER_V2, "v2")
    result = runner.invoke(app, ["log", "summarizer"])
    assert "v1" in result.stdout
    assert "v2" in result.stdout


# ---------------------------------------------------------------------------
# log
# ---------------------------------------------------------------------------


def test_log_unknown_prompt(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["log", "nonexistent"])
    assert result.exit_code == 1
    assert "nonexistent" in result.stdout


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_show_latest(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    result = runner.invoke(app, ["show", "summarizer"])
    assert result.exit_code == 0
    assert "summarizer" in result.stdout


def test_show_specific_version(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "v1")
    _stage_and_commit("summarizer", SUMMARIZER_V2, "v2")
    result = runner.invoke(app, ["show", "summarizer", "--version", "1"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


def test_diff_two_versions(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "v1")
    _stage_and_commit("summarizer", SUMMARIZER_V2, "v2")
    result = runner.invoke(app, ["diff", "summarizer"])
    assert result.exit_code == 0


def test_diff_single_version_warns(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "only one")
    result = runner.invoke(app, ["diff", "summarizer"])
    assert result.exit_code == 0
    assert "fewer than 2" in result.stdout


# ---------------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------------


def test_rollback_creates_new_version(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "v1")
    _stage_and_commit("summarizer", SUMMARIZER_V2, "v2")
    result = runner.invoke(app, ["rollback", "summarizer", "--version", "1"])
    assert result.exit_code == 0
    log_result = runner.invoke(app, ["log", "summarizer"])
    assert "v3" in log_result.stdout


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_shows_prompts(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1)
    _stage_and_commit("classifier", CLASSIFIER_V1)
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "summarizer" in result.stdout
    assert "classifier" in result.stdout


# ---------------------------------------------------------------------------
# env
# ---------------------------------------------------------------------------


def test_env_shows_default(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["env"])
    assert result.exit_code == 0
    assert "dev" in result.stdout


def test_env_set(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["env", "set", "staging"])
    assert result.exit_code == 0
    check = runner.invoke(app, ["env"])
    assert "staging" in check.stdout


def test_env_set_invalid(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["env", "set", "production"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


def test_export_json(isolated_dir: Path) -> None:
    import json

    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    out = isolated_dir / "export.json"
    result = runner.invoke(app, ["export", "summarizer", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["name"] == "summarizer"
    assert len(data["versions"]) == 1


# ---------------------------------------------------------------------------
# tag
# ---------------------------------------------------------------------------


def test_tag_version(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    result = runner.invoke(app, ["tag", "summarizer", "1", "stable"])
    assert result.exit_code == 0
    log_result = runner.invoke(app, ["log", "summarizer"])
    assert "stable" in log_result.stdout


def test_tag_duplicate_warns(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    runner.invoke(app, ["tag", "summarizer", "1", "stable"])
    result = runner.invoke(app, ["tag", "summarizer", "1", "stable"])
    assert result.exit_code == 0
    assert "already exists" in result.stdout


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def test_search_finds_content(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    result = runner.invoke(app, ["search", "summarization"])
    assert result.exit_code == 0
    assert "summarizer" in result.stdout


def test_search_no_results(isolated_dir: Path) -> None:
    runner.invoke(app, ["init"])
    _stage_and_commit("summarizer", SUMMARIZER_V1, "initial")
    result = runner.invoke(app, ["search", "xyzqwerty99"])
    assert result.exit_code == 0
    assert "No results" in result.stdout


# ---------------------------------------------------------------------------
# no init guard
# ---------------------------------------------------------------------------


def test_commands_fail_without_init(isolated_dir: Path) -> None:
    result = runner.invoke(app, ["log", "anything"])
    assert result.exit_code == 1
    assert "promptvc init" in result.stdout
