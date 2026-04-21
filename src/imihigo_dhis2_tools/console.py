from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def print_success(msg: str) -> None:
    console.print(f"[bold green]✓[/bold green] {msg}")


def print_error(msg: str) -> None:
    console.print(Panel(f"[red]{msg}[/red]", title="Error", border_style="red"))


def print_warning(msg: str) -> None:
    console.print(f"[yellow]![/yellow] {msg}")


def print_step(msg: str) -> None:
    console.print(f"[cyan]→[/cyan] {msg}")


def make_spinner(description: str) -> Progress:
    return Progress(SpinnerColumn(), TextColumn(description), console=console, transient=True)


def print_import_summary(stats: dict) -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Type")
    table.add_column("Created", justify="right")
    table.add_column("Updated", justify="right")
    table.add_column("Ignored", justify="right")
    table.add_column("Deleted", justify="right")

    type_reports = stats.get("typeReports", [])
    if type_reports:
        for report in type_reports:
            klass = report.get("klass", "").split(".")[-1]
            s = report.get("stats", {})
            if any(s.get(k, 0) > 0 for k in ("created", "updated", "ignored", "deleted")):
                table.add_row(
                    klass,
                    str(s.get("created", 0)),
                    str(s.get("updated", 0)),
                    str(s.get("ignored", 0)),
                    str(s.get("deleted", 0)),
                )
    else:
        s = stats.get("stats", stats)
        table.add_row(
            "Total",
            str(s.get("created", 0)),
            str(s.get("updated", 0)),
            str(s.get("ignored", 0)),
            str(s.get("deleted", 0)),
        )

    console.print(table)
