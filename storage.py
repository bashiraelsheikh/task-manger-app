import json
import os
from factory import task_from_dict


def save_tasks(tasks, filepath="tasks.json"):
    with open(filepath, "w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)


def load_tasks(filepath="tasks.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return [task_from_dict(d) for d in json.load(f)]
