"""
models.py
---------
The heart of the system — Task and its three children.

Design decisions:
  - Task is abstract; you can't create a raw Task (use subclasses).
  - Each subclass adds its own flavour without breaking the base contract.
  - __repr__ is for developers, __str__ is for humans.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional, Set

from task_manager.exceptions import (
    InvalidTaskError,
    InvalidPriorityError,
    InvalidDateError,
)

# ── Constants ──────────────────────────────────────────────────────────────────

VALID_PRIORITIES = ("low", "medium", "high")

VALID_INTERVALS = ("daily", "weekly", "monthly")


# ── Base Task ──────────────────────────────────────────────────────────────────

class Task(ABC):
    """
    The blueprint every task inherits from.

    Responsibilities:
      - Hold the shared state: id, title, description, done-flag, tags.
      - Define the interface that all subclasses must honour.
      - Provide sensible defaults and human-readable output.

    Cannot be instantiated directly — always use a subclass.
    """

    def __init__(self, title: str, description: str = "", tags: Optional[Set[str]] = None):
        if not title or not title.strip():
            raise InvalidTaskError("a task must have a title — even a short one")

        self._id: str = str(uuid.uuid4())[:8]          # Short, readable ID (8 chars)
        self._title: str = title.strip()
        self._description: str = description.strip()
        self._completed: bool = False
        self._created_at: datetime = datetime.now()
        self._tags: Set[str] = set(tags) if tags else set()
        self._observers: list = []                       # For the Observer pattern

    # ── Properties (encapsulation) ─────────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value or not value.strip():
            raise InvalidTaskError("title can't be empty")
        self._title = value.strip()
        self._notify_observers("title updated")

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value.strip()
        self._notify_observers("description updated")

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def tags(self) -> Set[str]:
        return self._tags.copy()           # Return a copy — protect the internal set

    # ── Observer wiring ────────────────────────────────────────────────────────

    def attach_observer(self, observer):
        """Register someone who wants to hear about changes to this task."""
        self._observers.append(observer)

    def detach_observer(self, observer):
        """Unregister a listener."""
        self._observers.remove(observer)

    def _notify_observers(self, event: str):
        """Tell every listener what just changed."""
        for observer in self._observers:
            observer.update(self, event)

    # ── Behaviour ──────────────────────────────────────────────────────────────

    def complete(self):
        """Mark this task as done. Can only be done once."""
        if self._completed:
            raise InvalidTaskError(f"'{self._title}' is already marked as done")
        self._completed = True
        self._notify_observers("completed")

    def add_tag(self, tag: str):
        """Attach a label to this task (e.g. 'work', 'urgent')."""
        self._tags.add(tag.lower().strip())
        self._notify_observers(f"tag '{tag}' added")

    def remove_tag(self, tag: str):
        """Remove a label if it exists."""
        self._tags.discard(tag.lower().strip())

    def status_icon(self) -> str:
        """A small visual cue for the terminal."""
        return "✓" if self._completed else "○"

    # ── Serialization helpers ──────────────────────────────────────────────────

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert this task to a plain dictionary for JSON storage.
        Every subclass must implement this — they each have extra fields.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Rebuild a task from a dictionary (loaded from JSON).
        Each subclass knows how to reconstruct itself.
        """

    # ── Shared serialisation core (used by subclass to_dict) ──────────────────

    def _base_dict(self) -> dict:
        """The fields every task has in common."""
        return {
            "id": self._id,
            "type": self.__class__.__name__,
            "title": self._title,
            "description": self._description,
            "completed": self._completed,
            "created_at": self._created_at.isoformat(),
            "tags": list(self._tags),
        }

    def _load_base(self, data: dict):
        """Apply saved base fields back onto self (called by from_dict)."""
        self._id = data["id"]
        self._completed = data["completed"]
        self._created_at = datetime.fromisoformat(data["created_at"])
        self._tags = set(data.get("tags", []))

    # ── Human-readable output ──────────────────────────────────────────────────

    def __str__(self) -> str:
        tag_str = "  [" + ", ".join(sorted(self._tags)) + "]" if self._tags else ""
        return (
            f"[{self.status_icon()}] ({self._id}) {self._title}"
            f"{tag_str}"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, title={self._title!r})"


# ── DeadlineTask ───────────────────────────────────────────────────────────────

class DeadlineTask(Task):
    """
    A task that needs to be done by a specific date.
    It knows how much time you have left — and will tell you honestly.
    """

    def __init__(
        self,
        title: str,
        deadline: str,          # Expects 'YYYY-MM-DD'
        description: str = "",
        tags: Optional[Set[str]] = None,
    ):
        super().__init__(title, description, tags)
        self._deadline: date = self._parse_deadline(deadline)

    def _parse_deadline(self, deadline_str: str) -> date:
        try:
            parsed = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateError(deadline_str)
        return parsed

    @property
    def deadline(self) -> date:
        return self._deadline

    @deadline.setter
    def deadline(self, value: str):
        self._deadline = self._parse_deadline(value)
        self._notify_observers("deadline changed")

    def days_remaining(self) -> int:
        """How many days until the deadline? Negative means overdue."""
        return (self._deadline - date.today()).days

    def urgency_label(self) -> str:
        """A human-readable urgency hint."""
        days = self.days_remaining()
        if days < 0:
            return f"OVERDUE by {abs(days)} day(s)"
        elif days == 0:
            return "DUE TODAY"
        elif days <= 3:
            return f"URGENT — {days} day(s) left"
        else:
            return f"{days} day(s) remaining"

    def to_dict(self) -> dict:
        d = self._base_dict()
        d["deadline"] = self._deadline.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "DeadlineTask":
        obj = cls(
            title=data["title"],
            deadline=data["deadline"],
            description=data.get("description", ""),
            tags=set(data.get("tags", [])),
        )
        obj._load_base(data)
        return obj

    def __str__(self) -> str:
        return super().__str__() + f"{self.urgency_label()}"


# ── PriorityTask ───────────────────────────────────────────────────────────────

class PriorityTask(Task):
    """
    A task ranked by importance: low, medium, or high.
    High priority tasks make themselves known — visually and structurally.
    """

    PRIORITY_WEIGHT = {"low": 1, "medium": 2, "high": 3}

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        description: str = "",
        tags: Optional[Set[str]] = None,
    ):
        super().__init__(title, description, tags)
        self._priority: str = self._validate_priority(priority)

    def _validate_priority(self, value: str) -> str:
        v = value.lower().strip()
        if v not in VALID_PRIORITIES:
            raise InvalidPriorityError(value)
        return v

    @property
    def priority(self) -> str:
        return self._priority

    @priority.setter
    def priority(self, value: str):
        self._priority = self._validate_priority(value)
        self._notify_observers(f"priority changed to {self._priority}")

    def priority_icon(self) -> str:
        return {"low": "↓", "medium": "→", "high": "↑"}[self._priority]

    def weight(self) -> int:
        """Numeric weight — useful for sorting."""
        return self.PRIORITY_WEIGHT[self._priority]

    def to_dict(self) -> dict:
        d = self._base_dict()
        d["priority"] = self._priority
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "PriorityTask":
        obj = cls(
            title=data["title"],
            priority=data.get("priority", "medium"),
            description=data.get("description", ""),
            tags=set(data.get("tags", [])),
        )
        obj._load_base(data)
        return obj

    def __str__(self) -> str:
        return super().__str__() + f"  {self.priority_icon()} {self._priority.upper()}"


# ── RecurringTask ──────────────────────────────────────────────────────────────

class RecurringTask(Task):
    """
    A task that comes back on a schedule — daily, weekly, or monthly.
    Completing it resets it for the next cycle, rather than closing it forever.
    """

    def __init__(
        self,
        title: str,
        interval: str = "weekly",   # 'daily', 'weekly', 'monthly'
        description: str = "",
        tags: Optional[Set[str]] = None,
    ):
        super().__init__(title, description, tags)
        self._interval: str = self._validate_interval(interval)
        self._recurrence_count: int = 0     # How many times has this cycled?

    def _validate_interval(self, value: str) -> str:
        v = value.lower().strip()
        if v not in VALID_INTERVALS:
            raise InvalidTaskError(
                f"'{value}' isn't a valid interval — use 'daily', 'weekly', or 'monthly'"
            )
        return v

    @property
    def interval(self) -> str:
        return self._interval

    @property
    def recurrence_count(self) -> int:
        return self._recurrence_count

    def complete(self):
        """
        Completing a recurring task doesn't retire it — it resets it.
        The recurrence count goes up; completed flag stays False.
        """
        if not self._completed:
            self._recurrence_count += 1
            self._notify_observers(
                f"completed cycle #{self._recurrence_count} — resets for next {self._interval} run"
            )
            # Deliberately NOT setting self._completed = True
            # Recurring tasks are never "done done"
        else:
            super().complete()   # Safety fallback

    def to_dict(self) -> dict:
        d = self._base_dict()
        d["interval"] = self._interval
        d["recurrence_count"] = self._recurrence_count
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "RecurringTask":
        obj = cls(
            title=data["title"],
            interval=data.get("interval", "weekly"),
            description=data.get("description", ""),
            tags=set(data.get("tags", [])),
        )
        obj._load_base(data)
        obj._recurrence_count = data.get("recurrence_count", 0)
        return obj

    def __str__(self) -> str:
        return (
            super().__str__()
            + f"  🔁 {self._interval}  (done {self._recurrence_count}×)"
        )
