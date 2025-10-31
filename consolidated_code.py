# ======
# task.py
# ======
'''
from typing import List, Optional, Dict, Any

from datetime import datetime


class Task:
    """
    Represents a task with title, description, due date, tags, status, and folder.
    """
    def __init__(
        self,
        title: str, 
        description: str, 
        due_date: str,
        tags: Optional[List[str]] = None, 
        status: str ="Pending", 
        folder: Optional[str] = None
    ) -> None:
        """
        Initializes a new Task instance.

        Args:
            title (str): The title of the task.
            description (str): A short description of the task.
            due_date (str): The due date of the task in 'YYYY-MM-DD' format.
            tags (list, optional): A list of tags associated with the task. Defaults to an empty list.
            status (str, optional): The current status of the task (e.g., 'Pending', 'Completed'). Defaults to "Pending".
            folder (str, optional): The folder name this task belongs to. Defaults to None.
        """
        self.title = title
        self.description = description
        self.due_date = due_date 
        self.tags = tags or []
        self.status = status
        self.folder = folder

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Task object into a dictionary.

        Returns:
            dict: A dictionary containing all task attributes.
        """
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tags": self.tags,
            "status": self.status,
            "folder": self.folder
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Task":
        """
        Creates a Task instance from a dictionary.

        Args:
            data (dict): A dictionary containing task data.

        Returns:
            Task: A Task object constructed from the dictionary data.
        """

        return Task(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data["due_date"],
            tags=data.get("tags", []),
            status=data.get("status", "Pending"),
            folder=data.get("folder")
        )

    def is_due_soon(self, days: int =1) -> bool:
        """
        Checks if the task is due within a given number of days.

        Args:
            days (int, optional): The number of days to check against. Defaults to 1.

        Returns:
            bool: True if the task is due within the given number of days, False otherwise.
        """

        if self.due_date:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            now = datetime.now()
            return (due - now).days <= days
        return False
        
    def is_overdue(self) -> bool:
        """
        Determines if the task is past its due date.

        Returns:
            bool: True if the task is overdue, False otherwise.
        """
        if self.due_date:
            due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return due < today
        return False
    
    def is_not_completed(self) -> bool:
        """
        Checks whether the task has not been completed.

        Returns:
            bool: True if the task status is not 'Completed', False otherwise.
        """
        return self.status != "Completed"
'''
# ===============
#task_manager.py
# ===============
'''
from typing import List, Optional, Tuple, Dict, Any
import json, os

from task import Task

class TaskManager:
    """
    Manages a collection of Task objects, providing functionality to
    load, save, add, edit, and delete tasks.
    """
    def __init__(self, filepath: str = "tasks.json") -> None:
        """
        Initialize the TaskManager and load tasks from a JSON file.

        Args:
            filepath (str): The location of the JSON file storing tasks.
        """

        self.filepath = filepath
        self.tasks: List[Task] = self.load_tasks()

    def load_tasks(self) -> List[Task]:
        """
        Load tasks from the JSON file.

        Returns:
            list: A list of Task objects loaded from the file.
        """

        if not os.path.exists(self.filepath):
            return []
        
        with open(self.filepath, "r") as f:
            data = json.load(f)
        return [Task.from_dict(item) for item in data]

    def save_tasks(self) -> None:
        """
        Save the current list of tasks to the JSON file.
        """

        with open(self.filepath, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def add_task(self, task: Task) -> None:
        """
        Add a new task and save it to the file.

        Args:
            task (Task): The Task object to be added.
        """
        
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, title: str) -> None:
        """
        Delete a task by title and update the file.

        Args:
            title (str): The title of the task to delete.
        """
        self.tasks = [t for t in self.tasks if t.title != title]
        self.save_tasks()

    def edit_task(self, title: str, new_data: Dict[str, Any]) -> None:
        """
        Edit an existing task and save the changes.

        Args:
            title (str): The title of the task to edit.
            new_data (dict): A dictionary containing updated task values.
        """
        for t in self.tasks:
            if t.title == title:
                for key, value in new_data.items():
                    setattr(t, key, value)
        self.save_tasks()

    def view_tasks(self, filter_by: Optional[Tuple[str, Any]] = None) -> List[Task]:
        """
        Retrieve all tasks or filter by a specific attribute.

        Args:
            filter_by (tuple, optional): A (key, value) pair used to filter tasks.

        Returns:
            list: A list of Task objects.
        """
        if not filter_by:
            return self.tasks
        return [t for t in self.tasks if getattr(t, filter_by[0]) == filter_by[1]]
    

    def find_task(self, title: str) -> Optional[Task]:
        """
        Find a task by title (case-insensitive).

        Args:
            title (str): The title of the task to find.

        Returns:
            Task or None: The matching Task object, or None if not found.
        """
        for task in self.tasks:
            if task.title.lower() == title.lower():
                return task
        return None
'''
#==========
#notifier.py
#==========
'''
import subprocess

def send_notification(title: str, message: str) -> None:
    """
    Sends a macOS desktop notification using AppleScript.

    Args:
        title (str): The title of the notification.
        message (str): The body message of the notification.

    Returns:
        None
    """
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}"'
    ])

'''
# ==================
# utils/background.py
# ==================
'''
import time
import threading

from typing import Optional, Set
from task_manager import TaskManager
from .helpers import notify_due_tasks

def start_background_notifier(
    manager: TaskManager,
    interval: int = 60,
    stop_flag: Optional[threading.Event] = None
) -> None:
    """
    Continuously checks tasks in the TaskManager and sends notifications for overdue or
    soon-due tasks. Designed to be run in a background thread.

    Args:
        manager (TaskManager): Instance of TaskManager containing all tasks.
        interval (int, optional): Number of seconds to wait between checks. Defaults to 60.
        stop_flag (Optional[threading.Event], optional): Thread-safe event to signal stopping
            the loop. If None, the loop runs indefinitely. Defaults to None.

    Returns:
        None
    """
    notified: Set[str] = set()  # Keep track of tasks already notified

    while stop_flag is None or not stop_flag.is_set():
        notify_due_tasks(manager, notified)
        time.sleep(interval)
'''
# ==============
#.utils/helpers.py
# ==============
'''
import os

from typing import Optional, Set
from task_manager import TaskManager
from notifier import send_notification

def clear_screen():
    # os.system('cls' if os.name == 'nt' else 'clear')  for other mac users
    os.system('clear')


def notify_due_tasks(manager: TaskManager, notified: Optional[Set[str]] = None) -> None:
    """
    Checks all tasks once and sends notifications for overdue or soon-due tasks.
    
    Args:
        manager (TaskManager): The TaskManager instance containing all tasks.
        notified (Optional[Set[str]], optional): A set of task titles already notified
            to prevent duplicate notifications. If None, a new empty set is used.

    Returns:
        None
    """
    if notified is None:
        notified = set()

    for task in manager.tasks:
        if task.due_date and task.is_not_completed():
            # Notify overdue tasks
            if task.is_overdue() and task.title not in notified:
                send_notification(
                    "Overdue Task",
                    f"'{task.title}' is past due! ({task.due_date})"
                )
                notified.add(task.title)

            # Notify tasks due soon (1 day before)
            elif task.is_due_soon(1) and task.title not in notified:
                send_notification(
                    "Task Reminder",
                    f"'{task.title}' is due tomorrow! ({task.due_date})"
                )
                notified.add(task.title)
'''
# =================
#.ptTest/test_task.py
# =================
'''
from datetime import datetime, timedelta
from task import Task

def test_task_initialization() -> None:
    """Verify that a Task object initializes correctly with all attributes."""
    task: Task = Task(
        title="Finish report",
        description="Complete the final report for submission",
        due_date="2025-11-01",
        tags=["work", "urgent"],
        status="Pending",
        folder="Office"
    )

    assert task.title == "Finish report"
    assert task.description == "Complete the final report for submission"
    assert task.due_date == "2025-11-01"
    assert task.tags == ["work", "urgent"]
    assert task.status == "Pending"
    assert task.folder == "Office"  


def test_to_dict_and_from_dict() -> None:
    """Ensure Task can be serialized to dict and reconstructed correctly."""
    data: dict[str, object] = {
        "title": "Buy groceries",
        "description": "Milk, eggs, and bread",
        "due_date": "2025-10-30",
        "tags": ["home", "shopping"],
        "status": "Pending",
        "folder": "Personal"
    }

    task: Task = Task.from_dict(data)
    assert isinstance(task, Task)

    result: dict[str, object] = task.to_dict()
    assert result == data


def test_is_due_soon_true() -> None:
    """Check that is_due_soon() returns True for tasks due within 1 day."""
    tomorrow: str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    task: Task = Task("Test due soon", "desc", tomorrow)
    assert task.is_due_soon() is True


def test_is_due_soon_false() -> None:
    """Check that is_due_soon() returns False for tasks due after several days."""
    next_week: str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    task: Task = Task("Test not due soon", "desc", next_week)
    assert task.is_due_soon() is False


def test_is_overdue_true() -> None:
    """Verify that is_overdue() returns True for past due dates."""
    yesterday: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    task: Task = Task("Overdue task", "desc", yesterday)
    assert task.is_overdue() is True


def test_is_overdue_false() -> None:
    """Verify that is_overdue() returns False for future due dates."""
    tomorrow: str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    task: Task = Task("Not overdue", "desc", tomorrow)
    assert task.is_overdue() is False


def test_is_not_completed() -> None:
    """Ensure is_not_completed() correctly identifies incomplete tasks."""
    task_pending: Task = Task("Task 1", "desc", "2025-10-30", status="Pending")
    task_completed: Task = Task("Task 2", "desc", "2025-10-30", status="Completed")

    assert task_pending.is_not_completed() is True
    assert task_completed.is_not_completed() is False
'''
# =====================
#.ptTest/test_manager.py
# =====================
'''
import os
import json
import pytest
from typing import List
from task import Task
from task_manager import TaskManager

TEST_FILE: str = "test_tasks.json"

@pytest.fixture(autouse=True)
def cleanup():
    """
    Fixture to clean up the test JSON file before and after each test.
    """
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


@pytest.fixture
def sample_tasks() -> List[Task]:
    """
    Fixture that provides a list of sample Task objects for testing.

    Returns:
        List[Task]: A list of three sample tasks.
    """
    return [
        Task(title="Task 1", description="Desc 1", due_date="2025-11-01", status="Pending"),
        Task(title="Task 2", description="Desc 2", due_date="2025-11-02", status="Completed"),
        Task(title="Task 3", description="Desc 3", due_date="2025-11-03", status="Pending"),
    ]


def test_add_and_load_tasks(sample_tasks: List[Task]) -> None:
    """
    Test adding tasks to the manager and loading them back from the JSON file.

    Args:
        sample_tasks (List[Task]): A list of tasks provided by the fixture.
    """
    manager = TaskManager(filepath=TEST_FILE)
    for task in sample_tasks:
        manager.add_task(task)

    # Reload manager to test if saving/loading works
    manager2 = TaskManager(filepath=TEST_FILE)
    assert len(manager2.tasks) == 3
    assert manager2.tasks[0].title == "Task 1"


def test_delete_task(sample_tasks: List[Task]) -> None:
    """
    Test deleting a task by title.

    Args:
        sample_tasks (List[Task]): A list of tasks provided by the fixture.
    """
    manager = TaskManager(filepath=TEST_FILE)
    for task in sample_tasks:
        manager.add_task(task)

    manager.delete_task("Task 2")
    titles = [t.title for t in manager.tasks]
    assert "Task 2" not in titles
    assert len(manager.tasks) == 2


def test_edit_task(sample_tasks: List[Task]) -> None:
    """
    Test editing a task's attributes.

    Args:
        sample_tasks (List[Task]): A list of tasks provided by the fixture.
    """
    manager = TaskManager(filepath=TEST_FILE)
    for task in sample_tasks:
        manager.add_task(task)

    manager.edit_task("Task 1", {"status": "Completed", "description": "Updated"})
    task = manager.find_task("Task 1")
    assert task is not None, "Task not found"
    assert task.status == "Completed"
    assert task.description == "Updated"


def test_view_tasks_with_filter(sample_tasks: List[Task]) -> None:
    """
    Test viewing tasks, both with and without filtering.

    Args:
        sample_tasks (List[Task]): A list of tasks provided by the fixture.
    """
    manager = TaskManager(filepath=TEST_FILE)
    for task in sample_tasks:
        manager.add_task(task)

    # Test filtered view
    pending_tasks = manager.view_tasks(("status", "Pending"))
    assert len(pending_tasks) == 2
    for t in pending_tasks:
        assert t.status == "Pending"

    # Test view all
    all_tasks = manager.view_tasks()
    assert len(all_tasks) == 3


def test_find_task(sample_tasks: List[Task]) -> None:
    """
    Test finding a task by title (case-insensitive) and returning None for missing tasks.

    Args:
        sample_tasks (List[Task]): A list of tasks provided by the fixture.
    """
    manager = TaskManager(filepath=TEST_FILE)
    for task in sample_tasks:
        manager.add_task(task)

    task = manager.find_task("task 3")
    assert task is not None
    assert task.title == "Task 3"

    task_none = manager.find_task("Nonexistent")
    assert task_none is None

'''
# =====================
#.ptTest/test_notifier.py
# =====================
'''
# tests/test_notifier.py
import pytest
from unittest.mock import patch

import threading
import time
from typing import Set, Optional

from task import Task
from task_manager import TaskManager
from notifier import send_notification
from utils.background import start_background_notifier
from utils.helpers import notify_due_tasks

@pytest.fixture
def sample_manager() -> TaskManager:
    """
    Provides a TaskManager instance with sample tasks for testing notifications.

    Returns:
        TaskManager: Instance containing overdue and due-soon tasks.
    """
    manager = TaskManager()
    # Task overdue in the past
    manager.tasks.append(Task("Overdue Task", "desc", "2000-01-01", []))
    # Task due soon (adjust date to match is_due_soon logic if needed)
    manager.tasks.append(Task("Due Soon Task", "desc", "2099-12-31", []))
    return manager



def test_send_notification_calls_subprocess() -> None:
    """
    Tests that send_notification calls subprocess.run with the correct arguments.
    """
    with patch("subprocess.run") as mock_run:
        send_notification("Hello", "World")

        # Verify subprocess.run was called once
        mock_run.assert_called_once_with([
            "osascript", "-e",
            'display notification "World" with title "Hello"'
        ])



def test_notify_due_tasks_calls_send_notification(sample_manager: TaskManager) -> None:
    """
    Tests that notify_due_tasks calls send_notification for tasks that are overdue or due soon.

    Args:
        sample_manager (TaskManager): Fixture containing sample tasks.

    Returns:
        None
    """
    notified_set: Set[str] = set()

    with patch("utils.helpers.send_notification") as mock_notify:
        notify_due_tasks(sample_manager, notified_set)

        # Assert that at least one notification was triggered
        assert mock_notify.call_count >= 1

        # check arguments of the first call
        called_args = mock_notify.call_args[0]
        assert "Task" in called_args[0]


def test_start_background_notifier_runs_once(sample_manager: TaskManager) -> None:
    """
    Tests that start_background_notifier can run in a background thread and triggers notifications.

    Args:
        sample_manager (TaskManager): Fixture containing sample tasks.

    Returns:
        None
    """
    stop_flag: threading.Event = threading.Event()

    with patch("utils.helpers.send_notification") as mock_notify:
        def run_notifier() -> None:
            start_background_notifier(sample_manager, interval=1, stop_flag=stop_flag)

        thread = threading.Thread(target=run_notifier)
        thread.start()

        # Let the thread run briefly, then stop it
        time.sleep(0.5)
        stop_flag.set()
        thread.join()

        # Assert that at least one notification was triggered
        assert mock_notify.call_count >= 1

'''
