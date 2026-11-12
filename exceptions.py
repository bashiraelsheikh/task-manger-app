class TaskNotFoundError(Exception):
    def __init__(self, task_id):
        super().__init__(f"Task '{task_id}' not found.")

class InvalidTaskError(Exception):
    def __init__(self, message="Invalid task."):
        super().__init__(message)
