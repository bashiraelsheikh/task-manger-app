import unittest
import os
from models import Task, DeadlineTask, PriorityTask, RecurringTask
from manager import TaskManager
from factory import create_task, task_from_dict
from observer import LogListener
from decorator import UrgentTask
from iterator import TaskIterator, incomplete_tasks, tasks_by_tag
from exceptions import TaskNotFoundError, InvalidTaskError
from parser import parse_input, is_valid_date


class TestModels(unittest.TestCase):
    def test_task_created(self):
        t = Task("Do homework")
        self.assertEqual(t.title, "Do homework")
        self.assertFalse(t.completed)

    def test_task_complete(self):
        t = Task("Read book")
        t.complete()
        self.assertTrue(t.completed)

    def test_empty_title_raises(self):
        with self.assertRaises(InvalidTaskError):
            Task("")

    def test_unique_ids(self):
        self.assertNotEqual(Task("A").id, Task("B").id)

    def test_deadline_task(self):
        t = DeadlineTask("Submit", deadline="2026-05-30")
        self.assertEqual(t.deadline, "2026-05-30")
        self.assertEqual(t.to_dict()["type"], "DeadlineTask")

    def test_priority_task(self):
        t = PriorityTask("Fix bug", priority="high")
        self.assertEqual(t.priority, "high")

    def test_invalid_priority_raises(self):
        with self.assertRaises(InvalidTaskError):
            PriorityTask("Task", priority="extreme")

    def test_recurring_task(self):
        t = RecurringTask("Standup", interval="daily")
        self.assertEqual(t.interval, "daily")

    def test_invalid_interval_raises(self):
        with self.assertRaises(InvalidTaskError):
            RecurringTask("Task", interval="hourly")

    def test_tags(self):
        t = Task("Tagged")
        t.tags.add("work")
        self.assertIn("work", t.tags)

    def test_to_dict_has_all_keys(self):
        t = PriorityTask("Task", priority="low")
        d = t.to_dict()
        for key in ("id", "type", "title", "completed", "tags", "priority"):
            self.assertIn(key, d)


class TestFactory(unittest.TestCase):
    def test_create_each_type(self):
        for t, kwargs in [
            ("task", {"title": "T"}),
            ("deadline", {"title": "T", "deadline": "2026-01-01"}),
            ("priority", {"title": "T", "priority": "low"}),
            ("recurring", {"title": "T", "interval": "daily"}),
        ]:
            task = create_task(t, **kwargs)
            self.assertEqual(task.title, "T")

    def test_unknown_type_raises(self):
        with self.assertRaises(InvalidTaskError):
            create_task("ghost", title="X")

    def test_roundtrip_from_dict(self):
        original = PriorityTask("Original", priority="high")
        original.tags.add("work")
        restored = task_from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.priority, "high")
        self.assertIn("work", restored.tags)


class TestManager(unittest.TestCase):
    def setUp(self):
        self.m = TaskManager()

    def test_add_and_get(self):
        t = self.m.create("priority", title="Task", priority="low")
        self.assertEqual(self.m.get(t.id).title, "Task")

    def test_get_missing_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.m.get("fake-id")

    def test_delete(self):
        t = self.m.create("task", title="Gone")
        self.m.delete(t.id)
        with self.assertRaises(TaskNotFoundError):
            self.m.get(t.id)

    def test_complete(self):
        t = self.m.create("task", title="Done")
        self.m.complete(t.id)
        self.assertTrue(t.completed)

    def test_update(self):
        t = self.m.create("task", title="Old")
        self.m.update(t.id, title="New")
        self.assertEqual(t.title, "New")

    def test_update_bad_field_raises(self):
        t = self.m.create("task", title="T")
        with self.assertRaises(InvalidTaskError):
            self.m.update(t.id, fake_field="x")

    def test_count(self):
        self.m.create("task", title="T1")
        self.m.create("task", title="T2")
        self.assertEqual(self.m.count, 2)

    def test_incomplete(self):
        self.m.create("task", title="Pending")
        done = self.m.create("task", title="Done")
        self.m.complete(done.id)
        self.assertEqual(len(self.m.incomplete()), 1)

    def test_high_priority(self):
        self.m.create("priority", title="High", priority="high")
        self.m.create("priority", title="Low", priority="low")
        self.assertEqual(len(self.m.high_priority()), 1)

    def test_titles(self):
        self.m.create("task", title="Alpha")
        self.m.create("task", title="Beta")
        self.assertIn("Alpha", self.m.titles())

    def test_observer(self):
        listener = LogListener()
        self.m.events.subscribe(listener)
        self.m.create("task", title="Test")
        self.assertEqual(listener.log[0]["event"], "CREATED")
        self.assertEqual(listener.log[0]["title"], "Test")

    def test_save_and_load(self):
        path = "test_tasks_temp.json"
        m = TaskManager(filepath=path)
        m.create("priority", title="Saved", priority="high")
        m.save()
        m2 = TaskManager(filepath=path)
        m2.load()
        self.assertIn("Saved", m2.titles())
        os.remove(path)

    def test_create_from_input(self):
        t = self.m.create_from_input("title:Report type:priority priority:high")
        self.assertEqual(t.title, "Report")


class TestIterator(unittest.TestCase):
    def setUp(self):
        self.m = TaskManager()
        self.t1 = self.m.create("task", title="Pending")
        self.t2 = self.m.create("task", title="Done")
        self.m.complete(self.t2.id)
        self.t1.tags.add("work")

    def test_incomplete_iterator(self):
        result = list(incomplete_tasks(self.m.all_tasks()))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Pending")

    def test_tag_iterator(self):
        result = list(tasks_by_tag(self.m.all_tasks(), "work"))
        self.assertEqual(len(result), 1)

    def test_empty_raises_stop(self):
        with self.assertRaises(StopIteration):
            next(TaskIterator([]))


class TestDecorator(unittest.TestCase):
    def test_urgent_prefix(self):
        t = PriorityTask("Fix server", priority="high")
        u = UrgentTask(t)
        self.assertIn("URGENT", u.title)
        self.assertIn("Fix server", u.title)

    def test_custom_label(self):
        t = Task("Task")
        u = UrgentTask(t, label="HOT")
        self.assertIn("HOT", u.title)

    def test_delegates_complete(self):
        t = Task("Task")
        u = UrgentTask(t)
        u.complete()
        self.assertTrue(t.completed)

    def test_preserves_id(self):
        t = Task("Task")
        u = UrgentTask(t)
        self.assertEqual(u.id, t.id)


class TestParser(unittest.TestCase):
    def test_parse_fields(self):
        r = parse_input("title:Homework priority:high")
        self.assertEqual(r["title"], "Homework")
        self.assertEqual(r["priority"], "high")

    def test_missing_title_raises(self):
        with self.assertRaises(InvalidTaskError):
            parse_input("priority:high")

    def test_empty_input_raises(self):
        with self.assertRaises(InvalidTaskError):
            parse_input("   ")

    def test_valid_date(self):
        self.assertTrue(is_valid_date("2026-05-30"))

    def test_invalid_date(self):
        self.assertFalse(is_valid_date("30-05-2026"))


class TestExceptions(unittest.TestCase):
    def test_not_found_message(self):
        e = TaskNotFoundError("abc")
        self.assertIn("abc", str(e))

    def test_invalid_task_message(self):
        e = InvalidTaskError("bad input")
        self.assertIn("bad input", str(e))


if __name__ == "__main__":
    unittest.main(verbosity=2)
