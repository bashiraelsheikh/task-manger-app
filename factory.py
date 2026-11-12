"""
factory.py
----------
Factory Pattern — one place to create any task type.

Why use a factory here?
  Instead of doing: task = DeadlineTask(...) everywhere in the code,
  we ask the factory: "give me a deadline task" and it handles the rest.
  This means if we ever add a new task type, we only change ONE place.
"""

from task_manager.models import DeadlineTask, PriorityTask, RecurringTask
from task_manager.exceptions import InvalidTaskError


class TaskFactory:
    """
    Creates tasks by type name. The rest of the app never imports
    task classes directly — it just calls TaskFactory.create().
    """

    # Map string names to classes — easy to extend later
    _registry = {
        "deadline": DeadlineTask,
        "priority": PriorityTask,
        "recurring": RecurringTask,
    }

    @staticmethod
    def create(task_type: str, title: str, **kwargs):
        """
        Create a task by type.

        Usage:
            TaskFactory.create("deadline", "Submit report", deadline="2026-05-18")
            TaskFactory.create("priority", "Fix bug", priority="high")
            TaskFactory.create("recurring", "Gym", interval="daily")

        Raises InvalidTaskError if the type is not recognised.
        """
        task_type = task_type.lower().strip()

        if task_type not in TaskFactory._registry:
            supported = ", ".join(TaskFactory._registry.keys())
            raise InvalidTaskError(
                f"'{task_type}' is not a known task type. Try one of: {supported}"
            )

        cls = TaskFactory._registry[task_type]
        return cls(title=title, **kwargs)

    @staticmethod
    def register(task_type: str, cls):
        """
        Register a new task type at runtime.
        This is how you'd plug in a custom task class without editing this file.

        Example:
            TaskFactory.register("meeting", MeetingTask)
        """
        TaskFactory._registry[task_type.lower()] = cls

    @staticmethod
    def supported_types() -> list:
        """Return the list of currently supported task types."""
        return list(TaskFactory._registry.keys())

    @staticmethod
    def from_dict(data: dict):
        """
        Rebuild any task from a saved dictionary.
        Figures out which subclass to use from the 'type' field.
        Used when loading tasks from JSON.
        """
        task_type = data.get("type", "").lower()

        type_map = {
            "deadlinetask": DeadlineTask,
            "prioritytask": PriorityTask,
            "recurringtask": RecurringTask,
        }

        cls = type_map.get(task_type)
        if cls is None:
            raise InvalidTaskError(f"can't restore unknown task type '{task_type}'")

        return cls.from_dict(data)
