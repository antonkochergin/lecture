"""Сервисный слой — бизнес-логика, удобная для тестирования."""
from __future__ import annotations

from django.db.models import QuerySet, Q
from django.contrib.auth import get_user_model

from .models import Task, Category

User = get_user_model()


class TaskService:
    """Сервис для работы с задачами."""

    @staticmethod
    def create_task(owner, **kwargs) -> Task:
        """Создать задачу для пользователя."""
        return Task.objects.create(owner=owner, **kwargs)

    @staticmethod
    def filter_tasks(
        user,
        status: str | None = None,
        priority: str | None = None,
        category: Category | None = None,
        search: str | None = None,
    ) -> QuerySet[Task]:
        """Фильтрация задач пользователя."""
        qs = Task.objects.filter(owner=user)

        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return qs

    @staticmethod
    def bulk_complete(task_ids: list[int], user) -> int:
        """Массовое завершение задач. Возвращает кол-во обновлённых."""
        return Task.objects.filter(
            id__in=task_ids,
            owner=user,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
        ).update(status=Task.Status.DONE)

    @staticmethod
    def get_overdue_tasks(user) -> QuerySet[Task]:
        """Получить просроченные задачи."""
        from django.utils import timezone

        return Task.objects.filter(
            owner=user,
            due_date__lt=timezone.now(),
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
        )


class CategoryService:
    """Сервис для работы с категориями."""

    @staticmethod
    def get_or_create(name: str, slug: str) -> tuple[Category, bool]:
        return Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name},
        )

    @staticmethod
    def get_categories_with_task_count(user) -> list[dict]:
        """Категории с количеством задач пользователя."""
        from django.db.models import Count

        return list(
            Category.objects.filter(tasks__owner=user)
            .annotate(task_count=Count("tasks"))
            .values("id", "name", "slug", "task_count")
            .order_by("-task_count")
        )
