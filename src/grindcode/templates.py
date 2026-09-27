"""Built-in project templates for grindcode."""

TEMPLATES = {
    "fastapi": {
        "main.py": '"""{{name}} — FastAPI app."""\n\nfrom fastapi import FastAPI\n\napp = FastAPI(title="{{name}}")\n\n\n@app.get("/")\ndef index():\n    return {"message": "Hello from {{name}}"}\n\n\n@app.get("/health")\ndef health():\n    return {"status": "ok"}\n',
        "requirements.txt": "fastapi\nuvicorn[standard]\n",
        "requirements-dev.txt": "pytest\nhttpx\n",
        ".python-version": "3.12\n",
        "Procfile": "web: uvicorn main:app --host 0.0.0.0 --port $PORT\n",
        ".gitignore": "__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.pytest_cache/\n*.log\n.DS_Store\n.env\n",
        "README.md": "# {{name}}\n\nFastAPI project scaffolded by grindcode.\n\n## Dev\n\n    pip install -r requirements.txt -r requirements-dev.txt\n    uvicorn main:app --reload\n\n## Test\n\n    pytest -v\n",
        "static/index.html": '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>{{name}}</title>\n</head>\n<body>\n<h1>{{name}}</h1>\n<p>It works. Now build something.</p>\n</body>\n</html>\n',
        "tests/__init__.py": "",
        "tests/test_api.py": '"""Tests for {{name}}."""\n\nfrom fastapi.testclient import TestClient\n\nfrom main import app\n\n\ndef test_index():\n    client = TestClient(app)\n    r = client.get("/")\n    assert r.status_code == 200\n\n\ndef test_health():\n    client = TestClient(app)\n    r = client.get("/health")\n    assert r.status_code == 200\n    assert r.json() == {"status": "ok"}\n',
    },
    "cli": {
        "pyproject.toml": '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n\n[project]\nname = "{{package_name}}"\nversion = "0.1.0"\ndescription = "{{name}}"\nrequires-python = ">=3.11"\ndependencies = ["click>=8.1"]\n\n[project.scripts]\n{{package_name}} = "{{package_name}}.cli:main"\n\n[tool.hatch.build.targets.wheel]\npackages = ["src/{{package_name}}"]\n',
        "src/{{package_name}}/__init__.py": '"""{{name}}."""\n\n__version__ = "0.1.0"\n',
        "src/{{package_name}}/cli.py": '"""{{name}} CLI entry point."""\n\nimport click\n\n\n@click.group(invoke_without_command=True)\n@click.option("--version", is_flag=True)\n@click.pass_context\ndef main(ctx, version):\n    """{{name}} — command line tool."""\n    if version:\n        from {{package_name}} import __version__\n        click.echo(f"{{package_name}} {__version__}")\n        return\n    if ctx.invoked_subcommand is None:\n        click.echo("{{name}} — run --help to see commands.")\n\n\nif __name__ == "__main__":\n    main()\n',
        "tests/__init__.py": "",
        "tests/test_cli.py": '"""Tests for {{name}}."""\n\nfrom click.testing import CliRunner\n\nfrom {{package_name}}.cli import main\n\n\ndef test_help():\n    runner = CliRunner()\n    result = runner.invoke(main, ["--help"])\n    assert result.exit_code == 0\n',
        "README.md": "# {{name}}\n\nScaffolded by grindcode.\n\n## Install\n\n    pip install -e \".[dev]\"\n\n## Run\n\n    {{package_name}} --help\n",
        ".gitignore": "__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.pytest_cache/\n*.egg-info/\ndist/\nbuild/\n.env\n",
    },
}
