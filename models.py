import uuid
from exceptions import InvalidTaskError


class Task:
    def __init__(self, title, description=""):
        if not title:
            raise InvalidTaskError("Title cannot be empty.")
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.completed = False
        self.tags = set()

    def complete(self):
        self.completed = True

    def to_dict(self):
        return {
            "id": self.id,
            "type": "Task",
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "tags": list(self.tags),
        }

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"[{status}] {self.title} (ID: {self.id})"


class DeadlineTask(Task):
    def __init__(self, title, description="", deadline=None):
        super().__init__(title, description)
        self.deadline = deadline

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "DeadlineTask"
        data["deadline"] = self.deadline
        return data

    def __str__(self):
        return super().__str__() + f" | Due: {self.deadline}"


class PriorityTask(Task):
    LEVELS = ["low", "medium", "high", "critical"]

    def __init__(self, title, description="", priority="medium"):
        super().__init__(title, description)
        if priority not in self.LEVELS:
            raise InvalidTaskError(f"Priority must be one of {self.LEVELS}.")
        self.priority = priority

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "PriorityTask"
        data["priority"] = self.priority
        return data

    def __str__(self):
        return super().__str__() + f" | Priority: {self.priority}"


class RecurringTask(Task):
    INTERVALS = ["daily", "weekly", "monthly"]

    def __init__(self, title, description="", interval="weekly"):
        super().__init__(title, description)
        if interval not in self.INTERVALS:
            raise InvalidTaskError(f"Interval must be one of {self.INTERVALS}.")
        self.interval = interval

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "RecurringTask"
        data["interval"] = self.interval
        return data

    def __str__(self):
        return super().__str__() + f" | Every: {self.interval}"
