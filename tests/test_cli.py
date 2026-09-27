"""Tests for the grindcode CLI."""

from click.testing import CliRunner

from grindcode import __version__
from grindcode.cli import main
from grindcode.scaffold import package_name, render, scaffold


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


def test_new_unknown_template():
    runner = CliRunner()
    result = runner.invoke(main, ["new", "doesnotexist", "myapp"])
    assert result.exit_code == 1


def test_no_args_shows_panel():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "Grindcode" in result.output


def test_package_name_sanitizes():
    assert package_name("My Cool-App") == "my_cool_app"
    assert package_name("123go") == "app_123go"
    assert package_name("whats_for_dinner") == "whats_for_dinner"
    assert package_name("") == "app"


def test_render_substitutes():
    out = render("Hello {{name}}", {"name": "World"})
    assert out == "Hello World"


def test_scaffold_creates_files(tmp_path):
    target = tmp_path / "myapp"
    files = scaffold("fastapi", "myapp", target)
    assert "main.py" in files
    assert "requirements.txt" in files
    assert "tests/test_api.py" in files
    assert (target / "main.py").exists()
    assert "myapp" in (target / "main.py").read_text()


def test_scaffold_refuses_existing(tmp_path):
    target = tmp_path / "myapp"
    target.mkdir()
    (target / "existing.txt").write_text("hi")
    try:
        scaffold("fastapi", "myapp", target)
        assert False, "should have raised"
    except FileExistsError:
        pass


def test_scaffold_force_overwrites(tmp_path):
    target = tmp_path / "myapp"
    target.mkdir()
    (target / "existing.txt").write_text("hi")
    files = scaffold("fastapi", "myapp", target, force=True)
    assert len(files) > 0


def test_scaffold_unknown_template(tmp_path):
    try:
        scaffold("nope", "myapp", tmp_path / "x")
        assert False, "should have raised"
    except ValueError:
        pass


def test_cli_scaffold_creates_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["new", "fastapi", "myapp"])
    assert result.exit_code == 0
    assert (tmp_path / "myapp" / "main.py").exists()
