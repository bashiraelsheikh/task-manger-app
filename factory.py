from models import Task, DeadlineTask, PriorityTask, RecurringTask
from exceptions import InvalidTaskError

TYPE_MAP = {
    "task": Task,
    "deadline": DeadlineTask,
    "priority": PriorityTask,
    "recurring": RecurringTask,
}


def create_task(task_type, **kwargs):
    cls = TYPE_MAP.get(task_type.lower())
    if cls is None:
        raise InvalidTaskError(f"Unknown type '{task_type}'. Choose from: {list(TYPE_MAP)}")
    return cls(**kwargs)


def task_from_dict(data):
    restore_map = {
        "Task": Task,
        "DeadlineTask": DeadlineTask,
        "PriorityTask": PriorityTask,
        "RecurringTask": RecurringTask,
    }
    cls = restore_map.get(data.get("type"))
    if cls is None:
        raise InvalidTaskError(f"Cannot restore unknown type: {data.get('type')}")
    kwargs = {k: v for k, v in data.items() if k not in ("id", "type", "completed", "tags")}
    task = cls(**kwargs)
    task.id = data["id"]
    task.completed = data["completed"]
    task.tags = set(data.get("tags", []))
    return task
