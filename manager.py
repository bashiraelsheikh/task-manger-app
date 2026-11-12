from observer import EventManager
from factory import create_task
from storage import save_tasks, load_tasks
from iterator import incomplete_tasks, tasks_by_tag
from exceptions import TaskNotFoundError, InvalidTaskError
from parser import parse_input


class TaskManager:
    def __init__(self, filepath="tasks.json"):
        self._tasks = []
        self._index = {}
        self._tags = set()
        self._filepath = filepath
        self.events = EventManager()

    def add(self, task):
        self._tasks.append(task)
        self._index[task.id] = task
        self._tags.update(task.tags)
        self.events.notify("CREATED", task)
        return task

    def create(self, task_type, **kwargs):
        return self.add(create_task(task_type, **kwargs))

    def create_from_input(self, raw, default_type="priority"):
        fields = parse_input(raw)
        task_type = fields.pop("type", default_type)
        if "due" in fields:
            fields["deadline"] = fields.pop("due")
        return self.create(task_type, **fields)

    def get(self, task_id):
        if task_id not in self._index:
            raise TaskNotFoundError(task_id)
        return self._index[task_id]

    def delete(self, task_id):
        task = self.get(task_id)
        self._tasks.remove(task)
        del self._index[task_id]
        self.events.notify("DELETED", task)

    def complete(self, task_id):
        task = self.get(task_id)
        task.complete()
        self.events.notify("COMPLETED", task)
        return task

    def update(self, task_id, **kwargs):
        task = self.get(task_id)
        for key, value in kwargs.items():
            if not hasattr(task, key):
                raise InvalidTaskError(f"Task has no attribute '{key}'.")
            setattr(task, key, value)
        self.events.notify("UPDATED", task)
        return task

    def all_tasks(self):
        return list(self._tasks)

    def incomplete(self):
        return list(incomplete_tasks(self._tasks))

    def by_tag(self, tag):
        return list(tasks_by_tag(self._tasks, tag))

    def high_priority(self):
        return list(filter(
            lambda t: hasattr(t, "priority") and t.priority in ("high", "critical"),
            self._tasks
        ))

    def titles(self):
        return list(map(lambda t: t.title, self._tasks))

    def save(self):
        save_tasks(self._tasks, self._filepath)

    def load(self):
        for task in load_tasks(self._filepath):
            self._tasks.append(task)
            self._index[task.id] = task
            self._tags.update(task.tags)

    @property
    def count(self):
        return len(self._tasks)
