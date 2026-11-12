# Task Manager CLI

A command-line task manager written in pure Python, built to practice object-oriented design, classic design patterns and unit testing. Tasks are saved to a JSON file, so they survive between sessions.

```
=== Task Manager ===
Choose: 2
  1. [✗] Submit report (ID: 0b5c5f88) | Due: 2026-12-02
  2. [✗] Fix login bug (ID: 3bd8d4e6) | Priority: high
```

## Features

- Four task types: basic, deadline, priority (low / medium / high / critical) and recurring (daily / weekly / monthly)
- Add, view, complete and delete tasks, and filter to incomplete ones
- Tags, plus filters by tag and by high priority
- Quick-add parser for one-line input such as `title:Gym type:recurring interval:daily`
- Input validation with clear custom error messages
- JSON persistence: tasks load on start and save on exit
- 41 unit tests, no external dependencies

## Design

| Concept | Where | What it does |
| --- | --- | --- |
| Inheritance and polymorphism | `models.py` | `DeadlineTask`, `PriorityTask` and `RecurringTask` extend `Task` and override `to_dict()` and `__str__()` |
| Factory pattern | `factory.py` | Creates any task type from a name and rebuilds tasks from saved JSON |
| Observer pattern | `observer.py` | `EventManager` notifies listeners when a task is created, completed, updated or deleted |
| Decorator pattern | `decorator.py` | `UrgentTask` wraps a task to add a label without changing the class |
| Iterator | `iterator.py` | `TaskIterator` walks tasks lazily, filtered by a condition |
| Custom exceptions | `exceptions.py` | `TaskNotFoundError` and `InvalidTaskError` for clear error handling |

## Run it

Requires Python 3.8 or newer. No packages to install.

```bash
git clone https://github.com/bashiraelsheikh/task-manager-cli.git
cd task-manager-cli
python main.py
```

## Run the tests

```bash
python -m unittest tests -v
```

## Project structure

```
main.py         Menu-driven command-line interface
manager.py      TaskManager: the central controller
models.py       Task classes
factory.py      Task creation and loading
observer.py     Event system
decorator.py    UrgentTask wrapper
iterator.py     Filtered task iteration
parser.py       Quick-add input parsing and date validation
storage.py      Save and load to JSON
exceptions.py   Custom errors
tests.py        Unit tests
```

## What I'd add next

- Sort tasks by deadline and warn about overdue ones
- Mark recurring tasks as done for the current period and roll them forward automatically

## Author

Bashira El-Sheikh, AI Engineering student at Istanbul University · [GitHub](https://github.com/bashiraelsheikh)
