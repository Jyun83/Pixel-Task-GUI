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
