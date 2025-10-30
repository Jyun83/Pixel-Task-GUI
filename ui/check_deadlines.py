from rich.console import Console
from rich.panel import Panel
from utils.helpers import clear_screen

from task_manager import TaskManager

console = Console()
manager = TaskManager()

def check_deadlines_interface() -> None:
    """
    Interface for checking and displaying tasks that are due soon or overdue.
    Sends desktop notifications for tasks that are near or past their due date.
    """
    clear_screen()
    console.print(Panel("[bold cyan]Checking Upcoming & Overdue Deadlines[/bold cyan]", border_style="cyan"))

    due_soon = [t for t in manager.tasks if t.is_due_soon()]
    overdue = [t for t in manager.tasks if t.is_overdue()]

    if not due_soon and not overdue:
        console.print("[green]No tasks due soon or overdue.[/green]")
    else:
        if overdue:
            console.print("\n[bold red] ⚠️  Overdue Tasks:[/bold red]")
            for t in overdue:
                console.print(f"[red]- {t.title} (Due: {t.due_date})[/red]")

        if due_soon:
            console.print("\n[bold yellow] ⏰  Tasks Due Soon:[/bold yellow]")
            for t in due_soon:
                console.print(f"[yellow]- {t.title} (Due: {t.due_date})[/yellow]")

    input("\nPress [Enter] to return to main menu...")
