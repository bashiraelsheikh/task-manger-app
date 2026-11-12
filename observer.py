class EventManager:
    def __init__(self):
        self._listeners = []

    def subscribe(self, listener):
        self._listeners.append(listener)

    def unsubscribe(self, listener):
        self._listeners.remove(listener)

    def notify(self, event, task):
        for listener in self._listeners:
            listener.on_event(event, task)


class ConsoleListener:
    def on_event(self, event, task):
        print(f"  [{event}] {task.title}")


class LogListener:
    def __init__(self):
        self.log = []

    def on_event(self, event, task):
        self.log.append({"event": event, "id": task.id, "title": task.title})
