from typing import List, Optional, Dict, Any

from datetime import datetime


class Task():
    """
    Represents a task with title, description, due date, tags, status, and folder.
    """
    def __init__(
        self,
        title: str, 
        description: str, 
        due_date: str,
        tags: Optional[List[str]] = None, 
        status: str ="Not Yet", 
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
        if not title.strip():
            raise ValueError("Title can not be empty")
        
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")

            except ValueError:
                raise ValueError("Due date must be in YYYY-MM-DD format")
            
        
        if status not in ("Not Yet", "Pending", "Completed"):
            raise ValueError(f"Status: {status} is invalid")
        
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
            due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            now = datetime.now().date()
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
    