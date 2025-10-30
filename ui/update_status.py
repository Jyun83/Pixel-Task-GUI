from InquirerPy import inquirer

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from utils.helpers import clear_screen
from ui.view_tasks import view_tasks_interface
from task_manager import TaskManager

console = Console()
manager = TaskManager()

def update_status_interface() -> None:
    """
    Allows user to update the status of a specific task.
    """
    clear_screen()
    title = Prompt.ask("Enter the title of the task to update")
    task = manager.find_task(title)

    if not task:
        console.print("[red]Task not found.[/red]")
        input("\nPress [Enter] to return...")
        return


    new_status = inquirer.select( #type: ignore
        message =  "Enter new status (Pending/In Progress/Completed)", 
        choices = ["Not Yet", "Pending", "Completed"],
        default=task.status
    ).execute()
    manager.edit_task(task.title, {"status": new_status})
    console.print("[green]Task status updated successfully![/green]")
    input("\nPress [Enter] to return...")

def update_menu() -> None:
    """
    Displays the update menu interface for viewing and updating task statuses.
    """
    clear_screen()
    while True:
        console.print(Panel(
            "[bold cyan]Update Menu[/bold cyan]\n"
            "1. View All Tasks\n"
            "2. Update Task Status\n"
            "3. Back",
        ))

        choice = Prompt.ask("Select an option")
        if choice == "1":
            view_tasks_interface()
        elif choice == "2":
            update_status_interface()
        elif choice == "3":
            break
        else:
            console.print("[red]Invalid option![/red]")
