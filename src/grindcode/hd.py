"""Heredoc-safe file writer for phones."""

import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()

DEFAULT_SENTINEL = ":end"


@click.command(name="hd")
@click.argument("path", type=click.Path())
@click.option("--append", "-a", is_flag=True, help="Append instead of overwrite")
@click.option(
    "--sentinel",
    "-s",
    default=DEFAULT_SENTINEL,
    show_default=True,
    help="Line that ends input",
)
def hd(path, append, sentinel):
    """Write a file line-by-line. End with the sentinel line.

    Example:

        grindcode hd notes.md

    Then type or paste your content, and finish with ':end'
    on its own line. No bash heredocs, no hanging prompts.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if append else "w"
    verb = "Appending to" if append else "Writing"

    console.print(f"[bold]{verb}[/] {target}")
    console.print(
        f"[dim]Type or paste your content. "
        f"End with [cyan]{sentinel}[/] on its own line.[/]"
    )
    console.print()

    lines = []
    try:
        while True:
            line = input()
            if line.strip() == sentinel:
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        console.print()
        console.print("[yellow]Cancelled — nothing written.[/]")
        sys.exit(130)

    content = "\n".join(lines)
    if lines:
        content += "\n"

    with open(target, mode) as f:
        f.write(content)

    console.print()
    console.print(
        f"[green]Wrote[/] {len(lines)} lines "
        f"({len(content)} bytes) to [bold]{target}[/]"
    )
