"""Safe git token management for mobile."""

import getpass
import os
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Prompt

console = Console()

CRED_FILE = Path.home() / ".git-credentials"
HOST = "github.com"


def _read_creds():
    """Parse the credential store. Returns dict host -> (user, token)."""
    creds = {}
    if not CRED_FILE.exists():
        return creds
    for line in CRED_FILE.read_text().splitlines():
        line = line.strip()
        if not line or "@" not in line:
            continue
        try:
            proto_user, rest = line.split("://", 1)
            userinfo, host = rest.rsplit("@", 1)
            user, token = userinfo.split(":", 1)
            creds[host] = (user, token)
        except ValueError:
            continue
    return creds


def _write_creds(creds):
    """Write credential store with 0600 permissions."""
    lines = [
        f"https://{user}:{token}@{host}"
        for host, (user, token) in creds.items()
    ]
    CRED_FILE.write_text("\n".join(lines) + ("\n" if lines else ""))
    os.chmod(CRED_FILE, 0o600)


def _mask(token):
    if len(token) <= 8:
        return "*" * len(token)
    return token[:4] + "..." + token[-4:]


@click.group()
def gtoken():
    """Manage git credentials for GitHub."""


@gtoken.command("set")
@click.option("--user", prompt=True, help="GitHub username")
def set_token(user):
    """Store a GitHub token in the credential file."""
    console.print(
        "[dim]Paste your Personal Access Token (input is hidden).[/]"
    )
    console.print(
        "[dim]Generate one at: https://github.com/settings/tokens[/]"
    )
    token = getpass.getpass("Token: ").strip()

    if not token:
        console.print("[red]Error:[/] empty token")
        raise SystemExit(1)

    creds = _read_creds()
    creds[HOST] = (user, token)
    _write_creds(creds)

    # Ensure git is configured to use the store
    subprocess.run(
        ["git", "config", "--global", "credential.helper", "store"],
        check=False,
    )

    console.print(
        f"[green]Stored[/] credentials for [bold]{user}[/] "
        f"({_mask(token)}) in {CRED_FILE}"
    )


@gtoken.command("status")
def status():
    """Show current git credential status."""
    creds = _read_creds()
    if HOST not in creds:
        console.print(f"[yellow]No credentials stored for {HOST}.[/]")
        console.print("[dim]Run: grindcode gtoken set[/]")
        return

    user, token = creds[HOST]
    console.print(f"Host:     [bold]{HOST}[/]")
    console.print(f"User:     [bold]{user}[/]")
    console.print(f"Token:    {_mask(token)}")

    helper = subprocess.run(
        ["git", "config", "--global", "--get", "credential.helper"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    console.print(f"Helper:   {helper or '[red]not set[/]'}")

    perms = oct(CRED_FILE.stat().st_mode)[-3:]
    ok = perms == "600"
    console.print(
        f"File:     {CRED_FILE} "
        f"[{'green' if ok else 'yellow'}]{perms}[/]"
    )


@gtoken.command("clear")
def clear():
    """Remove stored credentials for GitHub."""
    creds = _read_creds()
    if HOST in creds:
        del creds[HOST]
        _write_creds(creds)
        console.print(f"[green]Cleared[/] credentials for {HOST}.")
    else:
        console.print(f"[dim]No credentials stored for {HOST}.[/]")
