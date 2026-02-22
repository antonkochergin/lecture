from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task-list"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("task/new/", views.TaskCreateView.as_view(), name="task-create"),
    path("task/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("task/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task-update"),
    path("task/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task-delete"),
    path("task/<int:pk>/complete/", views.task_complete, name="task-complete"),
    path("api/stats/", views.api_task_stats, name="api-task-stats"),
]
