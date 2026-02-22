"""Тесты URL-маршрутизации."""
import pytest
from django.urls import reverse, resolve

from tasks import views


class TestURLResolve:
    @pytest.mark.parametrize("url_name,view_cls_or_func,kwargs", [
        ("task-list", views.TaskListView, {}),
        ("task-create", views.TaskCreateView, {}),
        ("task-detail", views.TaskDetailView, {"pk": 1}),
        ("task-update", views.TaskUpdateView, {"pk": 1}),
        ("task-delete", views.TaskDeleteView, {"pk": 1}),
        ("task-complete", views.task_complete, {"pk": 1}),
        ("dashboard", views.dashboard, {}),
        ("api-task-stats", views.api_task_stats, {}),
    ])
    def test_url_resolves(self, url_name, view_cls_or_func, kwargs):
        url = reverse(url_name, kwargs=kwargs)
        resolved = resolve(url)
        if hasattr(view_cls_or_func, "as_view"):
            # CBV — проверяем класс
            assert resolved.func.view_class is view_cls_or_func
        else:
            # FBV
            assert resolved.func is view_cls_or_func

    def test_task_list_root(self):
        assert reverse("task-list") == "/"

    def test_task_create_url(self):
        assert reverse("task-create") == "/task/new/"

    def test_dashboard_url(self):
        assert reverse("dashboard") == "/dashboard/"
