"""Tests for the grindcode CLI."""

from click.testing import CliRunner

from grindcode import __version__
from grindcode.cli import main


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_shows_commands():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "new" in result.output


def test_doctor_runs():
    runner = CliRunner()
    result = runner.invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "Python" in result.output
    assert "Git" in result.output


def test_new_lists_templates():
    runner = CliRunner()
    result = runner.invoke(main, ["new"])
    assert result.exit_code == 0
    assert "fastapi" in result.output
    assert "cli" in result.output


def test_new_requires_name():
    runner = CliRunner()
    result = runner.invoke(main, ["new", "fastapi"])
    assert result.exit_code == 1
    assert "project name required" in result.output


def test_new_scaffold_not_implemented():
    runner = CliRunner()
    result = runner.invoke(main, ["new", "fastapi", "myapp"])
    assert result.exit_code == 0
    assert "myapp" in result.output


def test_no_args_shows_panel():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "Grindcode" in result.output
