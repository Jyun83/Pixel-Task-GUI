from InquirerPy import inquirer

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from utils.helpers import clear_screen
from task_manager import TaskManager

console = Console()
manager = TaskManager()

def edit_task_details_interface() -> None:
    """
    Interface for editing an existing task’s details.
    """
    clear_screen()
    console.print(Panel("[bold cyan]Edit Task Details[/bold cyan]", border_style="cyan"))

    title = Prompt.ask("Enter the title of the task to edit")
    task = manager.find_task(title)

    if not task:
        console.print("[red]Task not found.[/red]")
        input("\nPress [Enter] to return...")
        return

    new_title = Prompt.ask("New title", default=task.title)
    new_desc = Prompt.ask("New description", default=task.description)
    new_due = Prompt.ask("New due date (YYYY-MM-DD)", default=task.due_date)
    new_status = inquirer.select( #type: ignore
        message =  "Enter new status (Pending/In Progress/Completed)", 
        choices = ["Not Yet", "Pending", "Completed"],
        default=task.status
    ).execute()
    new_folder = Prompt.ask("New folder", default=task.folder or "")
    new_tags = Prompt.ask("New tags (comma-separated)", default=",".join(task.tags))

    manager.edit_task(task.title, {
        "title": new_title,
        "description": new_desc,
        "due_date": new_due,
        "status": new_status,
        "folder": new_folder,
        "tags": [t.strip() for t in new_tags.split(",") if t.strip()]
    })

    console.print("[green]Task updated successfully![/green]")
    input("\nPress [Enter] to return...")
