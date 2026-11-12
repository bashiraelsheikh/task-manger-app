class UrgentTask:
    def __init__(self, task, label="URGENT"):
        self._task = task
        self._label = label

    @property
    def id(self):
        return self._task.id

    @property
    def title(self):
        return f"[{self._label}] {self._task.title}"

    @property
    def completed(self):
        return self._task.completed

    @property
    def tags(self):
        return self._task.tags

    def complete(self):
        self._task.complete()

    def to_dict(self):
        data = self._task.to_dict()
        data["label"] = self._label
        return data

    def __str__(self):
        return f"[{self._label}] {self._task}"
