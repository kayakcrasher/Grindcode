"""Tests for log, hd, and gtoken commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from grindcode import gtoken as gtoken_mod
from grindcode.cli import main


# ---------- log ----------

def test_log_reads_file(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("INFO up\nERROR down\nWARNING slow\n")
    runner = CliRunner()
    result = runner.invoke(main, ["log", str(f)])
    assert result.exit_code == 0
    assert "INFO up" in result.output
    assert "ERROR down" in result.output
    assert "WARNING slow" in result.output


def test_log_tail_limits(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("\n".join(f"INFO line{i}" for i in range(100)) + "\n")
    runner = CliRunner()
    result = runner.invoke(main, ["log", str(f), "--tail", "5"])
    assert result.exit_code == 0
    assert "line99" in result.output
    assert "line0" not in result.output


def test_log_summary_counts(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("INFO a\nINFO b\nERROR c\n")
    runner = CliRunner()
    result = runner.invoke(main, ["log", str(f)])
    assert "INFO: 2" in result.output
    assert "ERROR: 1" in result.output


def test_log_missing_file():
    runner = CliRunner()
    result = runner.invoke(main, ["log", "/nonexistent/nope.log"])
    assert result.exit_code != 0


# ---------- hd ----------

def test_hd_writes_file(tmp_path):
    target = tmp_path / "notes.md"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["hd", str(target)],
        input="line one\nline two\n:end\n",
    )
    assert result.exit_code == 0
    assert target.read_text() == "line one\nline two\n"


def test_hd_append(tmp_path):
    target = tmp_path / "notes.md"
    target.write_text("first\n")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["hd", str(target), "--append"],
        input="second\n:end\n",
    )
    assert result.exit_code == 0
    assert target.read_text() == "first\nsecond\n"


def test_hd_custom_sentinel(tmp_path):
    target = tmp_path / "notes.md"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["hd", str(target), "--sentinel", "DONE"],
        input="hello\nDONE\n",
    )
    assert result.exit_code == 0
    assert target.read_text() == "hello\n"


def test_hd_creates_parent_dirs(tmp_path):
    target = tmp_path / "deep" / "nested" / "file.txt"
    runner = CliRunner()
    result = runner.invoke(
        main, ["hd", str(target)], input="hi\n:end\n"
    )
    assert result.exit_code == 0
    assert target.exists()


# ---------- gtoken ----------

@pytest.fixture
def fake_creds(tmp_path, monkeypatch):
    """Redirect gtoken's credential file to a temp path."""
    cred_file = tmp_path / ".git-credentials"
    monkeypatch.setattr(gtoken_mod, "CRED_FILE", cred_file)
    # Avoid actually calling `git config`
    class FakeResult:
        stdout = "store"

    monkeypatch.setattr(
        gtoken_mod.subprocess, "run", lambda *a, **kw: FakeResult()
    )
    return cred_file


def test_gtoken_status_no_creds(fake_creds):
    runner = CliRunner()
    result = runner.invoke(main, ["gtoken", "status"])
    assert result.exit_code == 0
    assert "No credentials" in result.output


def test_gtoken_set_writes_file(fake_creds, monkeypatch):
    monkeypatch.setattr(
        gtoken_mod.getpass, "getpass", lambda prompt="": "ghp_testtoken123"
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["gtoken", "set", "--user", "kayakcrasher"]
    )
    assert result.exit_code == 0
    assert fake_creds.exists()
    content = fake_creds.read_text()
    assert "kayakcrasher" in content
    assert "ghp_testtoken123" in content


def test_gtoken_status_shows_token(fake_creds):
    fake_creds.write_text(
        "https://kayakcrasher:ghp_abcdefghij1234@github.com\n"
    )
    runner = CliRunner()
    result = runner.invoke(main, ["gtoken", "status"])
    assert result.exit_code == 0
    assert "kayakcrasher" in result.output
    assert "ghp_...1234" in result.output


def test_gtoken_clear(fake_creds):
    fake_creds.write_text(
        "https://user:token123456@github.com\n"
    )
    runner = CliRunner()
    result = runner.invoke(main, ["gtoken", "clear"])
    assert result.exit_code == 0
    assert "Cleared" in result.output
    assert fake_creds.read_text() == ""


def test_gtoken_clear_when_empty(fake_creds):
    runner = CliRunner()
    result = runner.invoke(main, ["gtoken", "clear"])
    assert result.exit_code == 0
    assert "No credentials" in result.output


def test_mask_short_token():
    from grindcode.gtoken import _mask
    assert _mask("short") == "*****"


def test_mask_long_token():
    from grindcode.gtoken import _mask
    assert _mask("ghp_abcdefghij1234") == "ghp_...1234"
