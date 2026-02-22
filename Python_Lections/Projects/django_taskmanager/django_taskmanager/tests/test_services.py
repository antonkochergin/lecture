"""Юнит-тесты сервисного слоя."""
import pytest
from datetime import timedelta
from django.utils import timezone

from tasks.models import Task
from tasks.services import TaskService, CategoryService
from tests.conftest import TaskFactory, CategoryFactory


# ── TaskService ──────────────────────────────────────────────────


class TestTaskServiceCreate:
    def test_create_task(self, user):
        task = TaskService.create_task(owner=user, title="Сервисная задача")
        assert task.pk is not None
        assert task.owner == user
        assert task.title == "Сервисная задача"

    def test_create_with_all_fields(self, user, category):
        due = timezone.now() + timedelta(days=3)
        task = TaskService.create_task(
            owner=user,
            title="Полная задача",
            description="Описание",
            priority=Task.Priority.HIGH,
            status=Task.Status.IN_PROGRESS,
            category=category,
            due_date=due,
        )
        assert task.priority == Task.Priority.HIGH
        assert task.category == category


class TestTaskServiceFilter:
    def test_filter_by_status(self, task_list, user):
        result = TaskService.filter_tasks(user, status=Task.Status.DONE)
        assert all(t.status == Task.Status.DONE for t in result)

    def test_filter_by_priority(self, task_list, user):
        result = TaskService.filter_tasks(user, priority=Task.Priority.CRITICAL)
        assert all(t.priority == Task.Priority.CRITICAL for t in result)

    def test_filter_by_category(self, task_list, user, category):
        result = TaskService.filter_tasks(user, category=category)
        assert all(t.category == category for t in result)

    def test_filter_by_search_title(self, db, user):
        TaskFactory(owner=user, title="Django проект")
        TaskFactory(owner=user, title="Flask проект")
        result = TaskService.filter_tasks(user, search="Django")
        assert result.count() == 1
        assert result.first().title == "Django проект"

    def test_filter_by_search_description(self, db, user):
        TaskFactory(owner=user, title="Задача", description="Нужен pytest")
        result = TaskService.filter_tasks(user, search="pytest")
        assert result.count() == 1

    def test_combined_filters(self, db, user, category):
        TaskFactory(
            owner=user,
            title="Django тест",
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
            category=category,
        )
        TaskFactory(
            owner=user,
            title="Django другой",
            status=Task.Status.DONE,
            priority=Task.Priority.HIGH,
            category=category,
        )
        result = TaskService.filter_tasks(
            user,
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
            category=category,
            search="Django",
        )
        assert result.count() == 1

    def test_empty_filters_return_all(self, task_list, user):
        result = TaskService.filter_tasks(user)
        assert result.count() == len(task_list)

    def test_isolation_between_users(self, task, other_user):
        result = TaskService.filter_tasks(other_user)
        assert result.count() == 0


class TestBulkComplete:
    def test_bulk_complete(self, db, user):
        t1 = TaskFactory(owner=user, status=Task.Status.TODO)
        t2 = TaskFactory(owner=user, status=Task.Status.IN_PROGRESS)
        t3 = TaskFactory(owner=user, status=Task.Status.DONE)
        updated = TaskService.bulk_complete([t1.pk, t2.pk, t3.pk], user)
        assert updated == 2  # t3 уже DONE

        t1.refresh_from_db()
        t2.refresh_from_db()
        assert t1.status == Task.Status.DONE
        assert t2.status == Task.Status.DONE

    def test_bulk_complete_other_user(self, task, other_user):
        updated = TaskService.bulk_complete([task.pk], other_user)
        assert updated == 0
        task.refresh_from_db()
        assert task.status == Task.Status.TODO


class TestGetOverdueTasks:
    def test_returns_overdue(self, overdue_task, user):
        result = TaskService.get_overdue_tasks(user)
        assert overdue_task in result

    def test_excludes_future_due(self, task, user):
        result = TaskService.get_overdue_tasks(user)
        assert task not in result

    def test_excludes_done(self, db, user):
        TaskFactory(
            owner=user,
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.DONE,
        )
        assert TaskService.get_overdue_tasks(user).count() == 0


# ── CategoryService ──────────────────────────────────────────────


class TestCategoryService:
    def test_get_or_create_new(self, db):
        cat, created = CategoryService.get_or_create("DevOps", "devops")
        assert created is True
        assert cat.name == "DevOps"

    def test_get_or_create_existing(self, category):
        cat, created = CategoryService.get_or_create("Работа", category.slug)
        assert created is False
        assert cat.pk == category.pk

    def test_categories_with_task_count(self, db, user):
        c1 = CategoryFactory(name="A", slug="a")
        c2 = CategoryFactory(name="B", slug="b")
        TaskFactory.create_batch(3, owner=user, category=c1)
        TaskFactory.create_batch(1, owner=user, category=c2)

        result = CategoryService.get_categories_with_task_count(user)
        assert len(result) == 2
        assert result[0]["task_count"] == 3
        assert result[1]["task_count"] == 1
