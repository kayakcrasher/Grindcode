"""Grindcode CLI entry point."""

import platform
import shutil
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from grindcode import __version__
from grindcode.scaffold import list_templates, scaffold

console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit.")
@click.pass_context
def main(ctx, version):
    """Grindcode Mobile Helper — tools for coding on your phone."""
    if version:
        console.print(f"grindcode [bold cyan]{__version__}[/]")
        return
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                "[bold]Grindcode Mobile Helper[/]\n"
                "[dim]Tools for coding on your phone.[/]\n\n"
                "Run [cyan]grindcode --help[/] to see commands.",
                border_style="cyan",
            )
        )


@main.command()
def doctor():
    """Check your phone dev environment for common problems."""
    console.print("[bold]Grindcode environment check[/]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")

    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 11)
    table.add_row("Python", "[green]OK[/]" if ok else "[red]FAIL[/]", f"{py} (need 3.11+)")

    table.add_row("Platform", "[green]OK[/]", platform.platform())

    is_termux = "com.termux" in sys.prefix
    table.add_row(
        "Termux",
        "[green]YES[/]" if is_termux else "[dim]no[/]",
        sys.prefix if is_termux else "not detected",
    )

    git_path = shutil.which("git")
    table.add_row("Git", "[green]OK[/]" if git_path else "[red]MISSING[/]", git_path or "pkg install git")

    pip_path = shutil.which("pip") or shutil.which("pip3")
    table.add_row("pip", "[green]OK[/]" if pip_path else "[red]MISSING[/]", pip_path or "pkg install python-pip")

    home = Path.home()
    home_ok = home.exists() and home.is_dir()
    table.add_row("Home dir", "[green]OK[/]" if home_ok else "[red]FAIL[/]", str(home))

    console.print(table)
    console.print()

    if ok and git_path and pip_path and home_ok:
        console.print("[green]All checks passed.[/]")
    else:
        console.print("[yellow]Some checks failed. Fix the red rows above.[/]")


@main.command()
@click.argument("template", required=False)
@click.argument("name", required=False)
@click.option("--force", is_flag=True, help="Overwrite target directory if it exists.")
def new(template, name, force):
    """Create a new project from a template.

    Example: grindcode new fastapi my-app
    """
    if not template:
        console.print("[bold]Available templates:[/]\n")
        for t in list_templates():
            console.print(f"  [cyan]{t}[/]")
        console.print()
        console.print("Usage: [dim]grindcode new <template> <name>[/]")
        return

    if not name:
        console.print("[red]Error:[/] project name required")
        console.print("Usage: [dim]grindcode new <template> <name>[/]")
        sys.exit(1)

    target = Path.cwd() / name

    try:
        files = scaffold(template, name, target, force=force)
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        console.print(f"Available: [cyan]{', '.join(list_templates())}[/]")
        sys.exit(1)
    except FileExistsError as e:
        console.print(f"[red]Error:[/] {e}")
        console.print("Use [cyan]--force[/] to overwrite.")
        sys.exit(1)

    console.print(f"[green]Created[/] {template} project at [bold]{target}[/]\n")
    for f in files:
        console.print(f"  [dim]{f}[/]")
    console.print()
    console.print("Next steps:")
    console.print(f"  [cyan]cd {name}[/]")
    console.print("  [cyan]pytest -v[/]")


if __name__ == "__main__":
    main()
