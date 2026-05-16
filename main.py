from manager import TaskManager
from observer import ConsoleListener
from exceptions import TaskNotFoundError, InvalidTaskError

manager = TaskManager()
manager.events.subscribe(ConsoleListener())


def show_tasks(tasks):
    if not tasks:
        print("  (no tasks)")
        return
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. {t}")


def pick_task():
    tasks = manager.all_tasks()
    show_tasks(tasks)
    try:
        n = int(input("Select number: ")) - 1
        return tasks[n] if 0 <= n < len(tasks) else None
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def add_task():
    print("Types: task / deadline / priority / recurring")
    t = input("Type: ").strip()
    title = input("Title: ").strip()
    try:
        if t == "deadline":
            due = input("Due date (YYYY-MM-DD): ").strip()
            manager.create("deadline", title=title, deadline=due)
        elif t == "priority":
            p = input("Priority (low/medium/high/critical): ").strip()
            manager.create("priority", title=title, priority=p)
        elif t == "recurring":
            i = input("Interval (daily/weekly/monthly): ").strip()
            manager.create("recurring", title=title, interval=i)
        else:
            manager.create("task", title=title)
    except InvalidTaskError as e:
        print(f"Error: {e}")


def main():
    print("=== Task Manager ===")
    try:
        manager.load()
        print(f"Loaded {manager.count} task(s).\n")
    except Exception:
        pass

    while True:
        print("\n1. Add task")
        print("2. View all tasks")
        print("3. Mark complete")
        print("4. Delete task")
        print("5. View incomplete only")
        print("6. Save & exit")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            add_task()
        elif choice == "2":
            show_tasks(manager.all_tasks())
        elif choice == "3":
            task = pick_task()
            if task:
                try:
                    manager.complete(task.id)
                except TaskNotFoundError as e:
                    print(f"Error: {e}")
        elif choice == "4":
            task = pick_task()
            if task:
                try:
                    manager.delete(task.id)
                except TaskNotFoundError as e:
                    print(f"Error: {e}")
        elif choice == "5":
            show_tasks(manager.incomplete())
        elif choice == "6":
            manager.save()
            print("Saved. Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
