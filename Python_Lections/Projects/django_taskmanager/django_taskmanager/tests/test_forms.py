"""Юнит-тесты форм."""
import pytest

from tasks.forms import TaskForm, TaskFilterForm, CategoryForm
from tests.conftest import CategoryFactory


class TestTaskForm:
    def test_valid_minimal(self, db):
        form = TaskForm(data={
            "title": "Тестовая задача",
            "priority": "medium",
            "status": "todo",
        })
        assert form.is_valid(), form.errors

    def test_title_too_short(self, db):
        form = TaskForm(data={
            "title": "Ab",
            "priority": "medium",
            "status": "todo",
        })
        assert not form.is_valid()
        assert "title" in form.errors

    def test_title_stripped(self, db):
        form = TaskForm(data={
            "title": "   Задача   ",
            "priority": "medium",
            "status": "todo",
        })
        assert form.is_valid()
        assert form.cleaned_data["title"] == "Задача"

    def test_invalid_priority(self, db):
        form = TaskForm(data={
            "title": "Задача",
            "priority": "invalid",
            "status": "todo",
        })
        assert not form.is_valid()

    def test_with_category(self, category):
        form = TaskForm(data={
            "title": "Задача",
            "priority": "high",
            "status": "in_progress",
            "category": category.pk,
        })
        assert form.is_valid()


class TestTaskFilterForm:
    def test_empty_is_valid(self, db):
        form = TaskFilterForm(data={})
        assert form.is_valid()

    def test_with_status(self, db):
        form = TaskFilterForm(data={"status": "todo"})
        assert form.is_valid()
        assert form.cleaned_data["status"] == "todo"

    def test_with_search(self, db):
        form = TaskFilterForm(data={"search": "django"})
        assert form.is_valid()

    def test_all_filters(self, category):
        form = TaskFilterForm(data={
            "status": "done",
            "priority": "high",
            "category": category.pk,
            "search": "test",
        })
        assert form.is_valid()


class TestCategoryForm:
    def test_valid(self, db):
        form = CategoryForm(data={
            "name": "Новая",
            "slug": "new",
        })
        assert form.is_valid()

    def test_duplicate_slug(self, category):
        form = CategoryForm(data={
            "name": "Другая",
            "slug": category.slug,
        })
        assert not form.is_valid()
        assert "slug" in form.errors
