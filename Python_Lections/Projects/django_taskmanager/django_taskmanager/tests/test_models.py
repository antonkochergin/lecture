"""Юнит-тесты моделей Task и Category."""
import pytest
from datetime import timedelta
from django.utils import timezone

from tasks.models import Task, Category
from tests.conftest import TaskFactory, CategoryFactory, UserFactory


# ── Category ─────────────────────────────────────────────────────


class TestCategoryModel:
    def help_func(self):
        return 1+1

    def test_str(self, category):
        assert str(category) == "Работа"

    def test_unique_slug(self, category, db):
        with pytest.raises(Exception):
            Category.objects.create(name="Другая", slug=category.slug)

    def test_ordering(self, db):
        CategoryFactory(name="Бета", slug="beta")
        CategoryFactory(name="Альфа", slug="alpha")
        names = list(Category.objects.values_list("name", flat=True))
        assert names == sorted(names)


# ── Task basic ───────────────────────────────────────────────────


class TestTaskModel:
    def test_str(self, task):
        assert str(task) == task.title

    def test_default_status(self, db, user):
        t = Task.objects.create(title="Тест", owner=user)
        assert t.status == Task.Status.TODO

    def test_default_priority(self, db, user):
        t = Task.objects.create(title="Тест", owner=user)
        assert t.priority == Task.Priority.MEDIUM

    def test_created_at_auto(self, task):
        assert task.created_at is not None

    def test_category_nullable(self, db, user):
        t = Task.objects.create(title="Без категории", owner=user)
        assert t.category is None


# ── is_overdue property ──────────────────────────────────────────


class TestIsOverdue:
    def test_overdue_when_past_due(self, overdue_task):
        assert overdue_task.is_overdue is True

    def test_not_overdue_when_future_due(self, task):
        assert task.is_overdue is False

    def test_not_overdue_when_done(self, db, user):
        t = TaskFactory(
            owner=user,
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.DONE,
        )
        assert t.is_overdue is False

    def test_not_overdue_when_cancelled(self, db, user):
        t = TaskFactory(
            owner=user,
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.CANCELLED,
        )
        assert t.is_overdue is False

    def test_not_overdue_when_no_due_date(self, db, user):
        t = TaskFactory(owner=user, due_date=None)
        assert t.is_overdue is False


# ── complete / cancel ────────────────────────────────────────────


class TestTaskActions:
    def test_complete(self, task):
        task.complete()
        task.refresh_from_db()
        assert task.status == Task.Status.DONE

    def test_cancel(self, task):
        task.cancel()
        task.refresh_from_db()
        assert task.status == Task.Status.CANCELLED


# ── get_active_for_user ──────────────────────────────────────────


class TestGetActiveForUser:
    def test_returns_only_active(self, task_list, user):
        active = Task.get_active_for_user(user)
        for t in active:
            assert t.status in (Task.Status.TODO, Task.Status.IN_PROGRESS)

    def test_excludes_other_users(self, task, other_user):
        active = Task.get_active_for_user(other_user)
        assert active.count() == 0


# ── get_statistics ───────────────────────────────────────────────


class TestGetStatistics:
    def test_empty_stats(self, db, user):
        stats = Task.get_statistics(user)
        assert stats == {
            "total": 0,
            "done": 0,
            "active": 0,
            "cancelled": 0,
            "completion_rate": 0.0,
        }

    def test_stats_with_tasks(self, task_list, user):
        stats = Task.get_statistics(user)
        assert stats["total"] == len(task_list)
        assert stats["done"] + stats["active"] + stats["cancelled"] == stats["total"]

    def test_completion_rate(self, db, user):
        TaskFactory(owner=user, status=Task.Status.DONE)
        TaskFactory(owner=user, status=Task.Status.DONE)
        TaskFactory(owner=user, status=Task.Status.TODO)
        stats = Task.get_statistics(user)
        assert stats["completion_rate"] == pytest.approx(66.7, abs=0.1)
