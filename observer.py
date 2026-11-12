"""
observer.py
-----------
Observer Pattern — notify interested parties when a task changes.

How it works:
  - Observers "subscribe" to a task.
  - When something changes (title, completion, tags...), the task
    calls update() on every subscribed observer.
  - Observers can do whatever they want: print a log, send an email,
    update a UI, write to a file, etc.

This keeps tasks clean — they don't need to know what happens after
they change. They just shout "something changed!" and walk away.
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ── Base Observer interface ────────────────────────────────────────────────────

class Observer(ABC):
    """
    Anyone who wants to listen to task events must implement this.
    One method: update(task, event).
    """

    @abstractmethod
    def update(self, task, event: str):
        """
        Called automatically when the observed task changes.

        Args:
            task:  The Task object that changed.
            event: A short string describing what happened.
        """


# ── Concrete Observer 1: Console Logger ───────────────────────────────────────

class ConsoleNotifier(Observer):
    """
    Prints a notification to the terminal when a task changes.
    Simple and useful for development / demo purposes.
    """

    def update(self, task, event: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"  [{timestamp}] Task '{task.title}' — {event}")


# ── Concrete Observer 2: Event History Log ────────────────────────────────────

class EventLogger(Observer):
    """
    Keeps a running history of every event that happened across all tasks.
    You can query the log to see what changed and when.

    Useful for: audit trails, undo features, debugging.
    """

    def __init__(self):
        self._log: list[dict] = []

    def update(self, task, event: str):
        entry = {
            "time": datetime.now().isoformat(),
            "task_id": task.id,
            "task_title": task.title,
            "event": event,
        }
        self._log.append(entry)

    def get_history(self, task_id: str = None) -> list[dict]:
        """
        Return all logged events, optionally filtered by task ID.
        """
        if task_id:
            return [e for e in self._log if e["task_id"] == task_id]
        return list(self._log)

    def print_history(self):
        """Print the full event log in a readable format."""
        if not self._log:
            print("  No events recorded yet.")
            return
        for entry in self._log:
            t = entry["time"][11:19]   # just HH:MM:SS
            print(f"  [{t}] ({entry['task_id']}) {entry['task_title']} → {entry['event']}")

    def clear(self):
        self._log.clear()


# ── Concrete Observer 3: Completion Tracker ───────────────────────────────────

class CompletionTracker(Observer):
    """
    Watches for 'completed' events and keeps a count.
    Could be extended to trigger rewards, streaks, or reports.
    """

    def __init__(self):
        self._completed_ids: set = set()

    def update(self, task, event: str):
        if event == "completed":
            self._completed_ids.add(task.id)

    @property
    def count(self) -> int:
        return len(self._completed_ids)

    def has_completed(self, task_id: str) -> bool:
        return task_id in self._completed_ids
