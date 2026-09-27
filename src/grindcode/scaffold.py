"""Project scaffolding logic."""

import re
from pathlib import Path

from grindcode.templates import TEMPLATES


def package_name(name: str) -> str:
    """Turn a project name into a valid Python package name."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    if not cleaned:
        return "app"
    if cleaned[0].isdigit():
        cleaned = "app_" + cleaned
    return cleaned


def render(text: str, context: dict) -> str:
    """Replace {{key}} placeholders in text with context values."""
    def sub(match):
        key = match.group(1)
        return str(context.get(key, match.group(0)))
    return re.sub(r"\{\{(\w+)\}\}", sub, text)


def list_templates():
    """Return sorted list of available template names."""
    return sorted(TEMPLATES.keys())


def scaffold(template: str, name: str, target: Path, force: bool = False):
    """Create a project from a template."""
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template: {template}")

    target = Path(target)

    if target.exists() and target.is_dir() and any(target.iterdir()):
        if not force:
            raise FileExistsError(
                f"Directory '{target}' already exists and is not empty"
            )

    context = {
        "name": name,
        "package_name": package_name(name),
    }

    files_written = []
    for rel_path, content in TEMPLATES[template].items():
        rendered_path = render(rel_path, context)
        rendered_content = render(content, context)

        full_path = target / rendered_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(rendered_content)
        files_written.append(str(full_path.relative_to(target)))

    return files_written
