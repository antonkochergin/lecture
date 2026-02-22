"""Тесты представлений (views)."""
import json
import pytest
from django.urls import reverse

from tasks.models import Task
from tests.conftest import TaskFactory


# ── Аутентификация ───────────────────────────────────────────────


class TestAuthRequired:
    """Неавторизованный пользователь перенаправляется на логин."""

    @pytest.mark.parametrize("url_name,kwargs", [
        ("task-list", {}),
        ("task-create", {}),
        ("dashboard", {}),
        ("api-task-stats", {}),
    ])
    def test_redirect_to_login(self, client, url_name, kwargs):
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url


class TestTaskDetailAuthRequired:
    def test_redirect(self, client, task):
        url = reverse("task-detail", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 302


# ── TaskListView ─────────────────────────────────────────────────


class TestTaskListView:
    def test_status_200(self, auth_client):
        response = auth_client.get(reverse("task-list"))
        assert response.status_code == 200

    def test_shows_own_tasks(self, auth_client, task):
        response = auth_client.get(reverse("task-list"))
        assert task.title.encode() in response.content

    def test_hides_other_user_tasks(self, auth_client, other_user):
        other_task = TaskFactory(owner=other_user, title="Чужая задача")
        response = auth_client.get(reverse("task-list"))
        assert other_task.title.encode() not in response.content

    def test_filter_by_status(self, auth_client, user):
        TaskFactory(owner=user, status=Task.Status.DONE, title="Готовая")
        TaskFactory(owner=user, status=Task.Status.TODO, title="Новая")
        response = auth_client.get(reverse("task-list") + "?status=done")
        assert b"\xd0\x93\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x8f" in response.content  # "Готовая" UTF-8

    def test_context_has_stats(self, auth_client, task):
        response = auth_client.get(reverse("task-list"))
        assert "stats" in response.context
        assert "total" in response.context["stats"]

    def test_pagination(self, auth_client, user):
        TaskFactory.create_batch(25, owner=user)
        response = auth_client.get(reverse("task-list"))
        assert response.context["is_paginated"] is True
        assert len(response.context["tasks"]) == 20


# ── TaskDetailView ───────────────────────────────────────────────


class TestTaskDetailView:
    def test_status_200(self, auth_client, task):
        response = auth_client.get(reverse("task-detail", kwargs={"pk": task.pk}))
        assert response.status_code == 200

    def test_404_other_user_task(self, auth_client, other_user):
        t = TaskFactory(owner=other_user)
        response = auth_client.get(reverse("task-detail", kwargs={"pk": t.pk}))
        assert response.status_code == 404

    def test_404_nonexistent(self, auth_client):
        response = auth_client.get(reverse("task-detail", kwargs={"pk": 99999}))
        assert response.status_code == 404


# ── TaskCreateView ───────────────────────────────────────────────


class TestTaskCreateView:
    def test_get_form(self, auth_client):
        response = auth_client.get(reverse("task-create"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_create_task(self, auth_client, user):
        data = {
            "title": "Новая задача через форму",
            "priority": "high",
            "status": "todo",
            "description": "Описание",
        }
        response = auth_client.post(reverse("task-create"), data)
        assert response.status_code == 302
        assert Task.objects.filter(title="Новая задача через форму", owner=user).exists()

    def test_create_invalid(self, auth_client):
        response = auth_client.post(reverse("task-create"), {"title": "Ab"})
        assert response.status_code == 200  # re-render form


# ── TaskUpdateView ───────────────────────────────────────────────


class TestTaskUpdateView:
    def test_update(self, auth_client, task):
        data = {
            "title": "Обновлённый заголовок",
            "priority": "critical",
            "status": task.status,
        }
        response = auth_client.post(
            reverse("task-update", kwargs={"pk": task.pk}), data
        )
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.title == "Обновлённый заголовок"
        assert task.priority == Task.Priority.CRITICAL

    def test_cannot_update_other_user_task(self, auth_client, other_user):
        t = TaskFactory(owner=other_user)
        response = auth_client.post(
            reverse("task-update", kwargs={"pk": t.pk}),
            {"title": "Хак", "priority": "low", "status": "todo"},
        )
        assert response.status_code == 404


# ── TaskDeleteView ───────────────────────────────────────────────


class TestTaskDeleteView:
    def test_delete(self, auth_client, task):
        response = auth_client.post(reverse("task-delete", kwargs={"pk": task.pk}))
        assert response.status_code == 302
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_cannot_delete_other_user_task(self, auth_client, other_user):
        t = TaskFactory(owner=other_user)
        response = auth_client.post(reverse("task-delete", kwargs={"pk": t.pk}))
        assert response.status_code == 404
        assert Task.objects.filter(pk=t.pk).exists()


# ── task_complete view ───────────────────────────────────────────


class TestTaskCompleteView:
    def test_complete(self, auth_client, task):
        response = auth_client.get(reverse("task-complete", kwargs={"pk": task.pk}))
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.status == Task.Status.DONE

    def test_complete_other_user_404(self, auth_client, other_user):
        t = TaskFactory(owner=other_user)
        response = auth_client.get(reverse("task-complete", kwargs={"pk": t.pk}))
        assert response.status_code == 404


# ── Dashboard ────────────────────────────────────────────────────


class TestDashboard:
    def test_status_200(self, auth_client):
        response = auth_client.get(reverse("dashboard"))
        assert response.status_code == 200

    def test_context_has_stats(self, auth_client, task):
        response = auth_client.get(reverse("dashboard"))
        assert "stats" in response.context
        assert "overdue_tasks" in response.context


# ── API endpoint ─────────────────────────────────────────────────


class TestApiTaskStats:
    def test_returns_json(self, auth_client, task):
        response = auth_client.get(reverse("api-task-stats"))
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"
        data = json.loads(response.content)
        assert "total" in data
        assert "completion_rate" in data

    def test_correct_values(self, auth_client, user):
        TaskFactory(owner=user, status=Task.Status.DONE)
        TaskFactory(owner=user, status=Task.Status.TODO)
        response = auth_client.get(reverse("api-task-stats"))
        data = json.loads(response.content)
        assert data["total"] == 2
        assert data["done"] == 1
