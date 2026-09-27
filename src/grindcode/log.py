"""Pretty log reader for phone screens."""

from collections import Counter
from pathlib import Path

import click
from rich.console import Console

console = Console()

LEVELS = [
    ("CRITICAL", "bold red"),
    ("ERROR", "red"),
    ("FAIL", "red"),
    ("WARNING", "yellow"),
    ("WARN", "yellow"),
    ("INFO", "cyan"),
    ("DEBUG", "dim"),
]


def detect_level(line):
    upper = line.upper()
    for name, _ in LEVELS:
        if name in upper:
            return name
    return None


def color_for(level):
    for name, color in LEVELS:
        if name == level:
            return color
    return None


@click.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@click.option("--tail", "-n", default=50, show_default=True, help="Show last N lines")
@click.option("--all", "show_all", is_flag=True, help="Show all lines")
def log(path, tail, show_all):
    """Pretty-print a log file. Colors by level. Reads from PATH."""
    lines = Path(path).read_text(errors="replace").splitlines()

    if not show_all and tail > 0:
        lines = lines[-tail:]

    counts = Counter()
    for line in lines:
        lvl = detect_level(line)
        if lvl:
            counts[lvl] += 1
        color = color_for(lvl)
        if color:
            console.print(line, style=color, highlight=False)
        else:
            console.print(line, highlight=False)

    console.print()
    console.rule("Summary")
    if not counts:
        console.print("  [dim]no level markers found[/]")
    for name, _ in LEVELS:
        if counts.get(name):
            console.print(f"  [bold]{name}[/]: {counts[name]}")
