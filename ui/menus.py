from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from utils.helpers import clear_screen

from ui.add_task import add_task_interface
from ui.view_tasks import view_tasks_interface
from ui.edit_task import edit_task_details_interface
from ui.update_status import update_menu
from ui.delete_task import del_menu
from ui.check_deadlines import check_deadlines_interface

console = Console()

def main_menu() -> None:
    """
    Displays the main menu interface and handles user navigation.
    """
    while True:
        clear_screen()
        console.print(Panel(
            "[bold magenta]Main Menu[/bold magenta]\n"
            "1. Add Task\n"
            "2. View Tasks\n"
            "3. Edit Task\n"
            "4. Update Status\n"
            "5. Delete Task\n"
            "6. Check Deadlines\n"
            "7. Exit",
            border_style="magenta"
        ))

        choice = Prompt.ask("Select an option")

        if choice == "1":
            add_task_interface()
        elif choice == "2":
            view_tasks_interface()
        elif choice == "3":
            edit_task_details_interface()
        elif choice == "4":
            update_menu()
        elif choice == "5":
            del_menu()
        elif choice == "6":
            check_deadlines_interface()
        elif choice == "7":
            console.print("[bold green]Goodbye![/bold green]")
            break
        else:
            console.print("[red]Invalid choice! Try again.[/red]")
