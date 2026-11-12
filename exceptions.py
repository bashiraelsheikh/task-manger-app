"""
exceptions.py
-------------
Custom exceptions for the Task Manager.
We give each error a personality — clear, honest, and a little human.
"""


class TaskNotFoundError(Exception):
    """
    Raised when you try to touch a task that doesn't exist.
    Like reaching for your keys and finding an empty hook.
    """
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(
            f"Hmm, no task with ID '{task_id}' was found. "
            f"It may have been deleted, or it never existed."
        )


class InvalidTaskError(Exception):
    """
    Raised when task data is missing, malformed, or makes no sense.
    Like a to-do item that just says '???'.
    """
    def __init__(self, reason):
        self.reason = reason
        super().__init__(
            f"This task doesn't look right — {reason}. "
            f"Please double-check what you're submitting."
        )


class DuplicateTaskError(Exception):
    """
    Raised when someone tries to add the same task twice.
    One task is intentional. Two is a mistake.
    """
    def __init__(self, title):
        self.title = title
        super().__init__(
            f"A task called '{title}' already exists. "
            f"Try updating it instead of creating a duplicate."
        )


class InvalidPriorityError(Exception):
    """
    Raised when a priority level is not recognised.
    We only speak: 'low', 'medium', or 'high'.
    """
    def __init__(self, value):
        self.value = value
        super().__init__(
            f"'{value}' isn't a valid priority. "
            f"Stick to: 'low', 'medium', or 'high'."
        )


class InvalidDateError(Exception):
    """
    Raised when a deadline date is malformed or in the past.
    You can't deadline something that's already gone.
    """
    def __init__(self, date_str):
        self.date_str = date_str
        super().__init__(
            f"'{date_str}' isn't a valid deadline. "
            f"Use YYYY-MM-DD format, and make sure it's a future date."
        )
