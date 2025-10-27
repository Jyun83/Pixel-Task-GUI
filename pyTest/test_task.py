from datetime import datetime, timedelta
from task import Task

def test_task_initialization() -> None:
    """Verify that a Task object initializes correctly with all attributes."""
    task: Task = Task(
        title="Finish report",
        description="Complete the final report for submission",
        due_date="2025-11-01",
        tags=["work", "urgent"],
        status="Pendxing",
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