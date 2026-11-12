class TaskIterator:
    def __init__(self, tasks, condition=None):
        self._tasks = [t for t in tasks if condition is None or condition(t)]
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._tasks):
            raise StopIteration
        task = self._tasks[self._index]
        self._index += 1
        return task


def incomplete_tasks(tasks):
    return TaskIterator(tasks, lambda t: not t.completed)


def tasks_by_tag(tasks, tag):
    return TaskIterator(tasks, lambda t: tag in t.tags)
