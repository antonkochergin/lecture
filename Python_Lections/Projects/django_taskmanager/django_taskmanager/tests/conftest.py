"""Общие фикстуры и фабрики для тестов."""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

import pytest
import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task, Category

User = get_user_model()


# ── Factory Boy фабрики ──────────────────────────────────────────


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        skip_postgeneration_save = True
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        raw_password = extracted or "testpass123"
        obj.set_password(raw_password)
        if create:
            obj.save(update_fields=["password"])

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Категория {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    description = factory.Faker("sentence", locale="ru_RU")


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Задача #{n}")
    description = factory.Faker("paragraph", locale="ru_RU")
    priority = Task.Priority.MEDIUM
    status = Task.Status.TODO
    owner = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    due_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


# ── Pytest фикстуры ─────────────────────────────────────────────


@pytest.fixture
def user():
    """Обычный пользователь."""
    return UserFactory()


@pytest.fixture
def other_user():
    """Второй пользователь для проверки изоляции."""
    return UserFactory(username="other_user")


@pytest.fixture
def category():
    return CategoryFactory(name="Работа", slug="work")


@pytest.fixture
def task(user, category):
    """Одна задача."""
    return TaskFactory(owner=user, category=category)


@pytest.fixture
def task_list(user, category):
    """Набор задач разных статусов и приоритетов."""
    tasks = []
    for status, _ in Task.Status.choices:
        for priority, _ in Task.Priority.choices:
            tasks.append(
                TaskFactory(
                    owner=user,
                    category=category,
                    status=status,
                    priority=priority,
                )
            )
    return tasks


@pytest.fixture
def overdue_task(user):
    """Просроченная задача."""
    return TaskFactory(
        owner=user,
        due_date=timezone.now() - timedelta(days=1),
        status=Task.Status.TODO,
    )


@pytest.fixture
def auth_client(client, user):
    """Авторизованный тестовый клиент."""
    client.login(username=user.username, password="testpass123")
    return client
