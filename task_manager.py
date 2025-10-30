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
        self.tasks = self.load_tasks()
        
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


