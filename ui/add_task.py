from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from datetime import datetime

from task import Task
from task_manager import TaskManager
from utils.helpers import clear_screen

console = Console()
manager = TaskManager()


def add_task_interface() -> None:
    """
    Interface for adding a new task through user input.

    Performs interactive UI checks for basic validation (e.g., empty title, invalid date format),
    and relies on backend validation for strict rules.
    """
    clear_screen()
    console.print(Panel("[bold cyan]Add a New Task[/bold cyan]", border_style="cyan"))

    while True:
        try:
            # ---------------- Prompt user ----------------
            while True:
                title = Prompt.ask("Enter task title")
                if title.strip():
                    break
                console.print("[red]Title cannot be empty! Please try again.[/red]")

            description = Prompt.ask("Enter description", default="")

            while True:
                due_date_str = Prompt.ask("Enter due date (YYYY-MM-DD)")
                try:
                    dt = datetime.strptime(due_date_str, "%Y-%m-%d")

                except ValueError:
                    console.print("[red]Invalid date format! Use YYYY-MM-DD.[/red]")
                    continue

                if dt.date() < datetime.now().date():
                    console.print("[red]Due date cannot be in the past![/red]")
                    continue
                break


            tags_input = Prompt.ask("Enter tags (comma-separated)", default="")
            folder = Prompt.ask("Enter folder (optional)", default="")

            # ---------------- Prepare data ----------------
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            folder = folder or None

            # ---------------- Create task ----------------
            # Backend will still validate title, due date, etc.
            task = Task(
                title=title,
                description=description,
                due_date=due_date_str,
                tags=tags,
                folder=folder
            )

            # ---------------- Add to manager ----------------
            manager.add_task(task)
            console.print("[green]Task added successfully![/green]")
            input("\nPress [Enter] to return to main menu...")
            break  # Exit loop if task creation succeeds

        except ValueError as e:
            # Catch any backend validation errors and show to user
            console.print(f"[red]{e}[/red]\n")
