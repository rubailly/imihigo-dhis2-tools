from __future__ import annotations

import os
import sys

import click
import questionary
from dotenv import load_dotenv

from .console import console, print_error, print_success
from .dhis2.client import DHIS2Client
from . import commands

load_dotenv()


def _make_client(url: str | None, username: str | None, password: str | None) -> DHIS2Client | None:
    url = url or os.getenv("DHIS2_BASE_URL", "")
    username = username or os.getenv("DHIS2_USERNAME", "")
    password = password or os.getenv("DHIS2_PASSWORD", "")

    if not all([url, username, password]):
        print_error("URL, username, and password are all required.")
        return None

    client = DHIS2Client(url, username, password)
    ok, info = client.test_connection()
    if not ok:
        print_error(f"Connection failed: {info}")
        return None

    print_success(f"Connected: {info}")
    return client


def _prompt_credentials() -> tuple[str, str, str]:
    url = questionary.text(
        "DHIS2 URL:", default=os.getenv("DHIS2_BASE_URL", "")
    ).ask()
    if url is None:
        sys.exit(0)

    username = questionary.text(
        "Username:", default=os.getenv("DHIS2_USERNAME", "")
    ).ask()
    if username is None:
        sys.exit(0)

    password = questionary.password("Password:").ask()
    if password is None:
        sys.exit(0)

    return url, username, password


def _interactive_menu() -> None:
    console.print("\n[bold blue]Imihigo DHIS2 Tools[/bold blue]")
    console.print("Manage Eastern Province Imihigo datasets on any DHIS2 instance\n")

    url, username, password = _prompt_credentials()
    client = _make_client(url, username, password)
    if client is None:
        return

    console.print()
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "install  — Create org units and import all dataset metadata",
                "seed     — Seed demo data values into installed datasets",
                "clean    — Remove everything this tool created",
                "exit",
            ],
        ).ask()

        if choice is None or "exit" in choice:
            break
        elif "install" in choice:
            from .commands import install
            console.print()
            install.run(client)
        elif "seed" in choice:
            from .commands import seed
            console.print()
            seed.run(client)
        elif "clean" in choice:
            from .commands import clean
            console.print()
            clean.run(client)

        console.print()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--url", envvar="DHIS2_BASE_URL", default=None, help="DHIS2 base URL")
@click.option("--username", "-u", envvar="DHIS2_USERNAME", default=None, help="Username")
@click.option("--password", "-p", envvar="DHIS2_PASSWORD", default=None, help="Password")
def main(ctx: click.Context, url: str | None, username: str | None, password: str | None) -> None:
    """Imihigo DHIS2 Tools — setup Eastern Province performance contract datasets."""
    ctx.ensure_object(dict)
    ctx.obj["url"] = url
    ctx.obj["username"] = username
    ctx.obj["password"] = password

    if ctx.invoked_subcommand is None:
        _interactive_menu()


@main.command()
@click.pass_context
def install(ctx: click.Context) -> None:
    """Create org units and import all Imihigo dataset metadata."""
    obj = ctx.obj or {}
    client = _make_client(obj.get("url"), obj.get("username"), obj.get("password"))
    if client is None:
        sys.exit(1)
    from .commands import install as install_cmd
    install_cmd.run(client)


@main.command()
@click.pass_context
def seed(ctx: click.Context) -> None:
    """Seed demo data values (requires install to have run first)."""
    obj = ctx.obj or {}
    client = _make_client(obj.get("url"), obj.get("username"), obj.get("password"))
    if client is None:
        sys.exit(1)
    from .commands import seed as seed_cmd
    seed_cmd.run(client)


@main.command()
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Remove all objects created by this tool."""
    obj = ctx.obj or {}
    client = _make_client(obj.get("url"), obj.get("username"), obj.get("password"))
    if client is None:
        sys.exit(1)
    from .commands import clean as clean_cmd
    clean_cmd.run(client)
