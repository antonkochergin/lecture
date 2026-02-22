from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Категория задач."""

    name = models.CharField("Название", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True, default="")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """Задача пользователя."""

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"
        CRITICAL = "critical", "Критический"

    class Status(models.TextChoices):
        TODO = "todo", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Выполнена"
        CANCELLED = "cancelled", "Отменена"

    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание", blank=True, default="")
    priority = models.CharField(
        "Приоритет",
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        "Статус",
        max_length=15,
        choices=Status.choices,
        default=Status.TODO,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Категория",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Владелец",
    )
    due_date = models.DateTimeField("Срок выполнения", null=True, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self) -> bool:
        """Просрочена ли задача."""
        if self.due_date and self.status not in (self.Status.DONE, self.Status.CANCELLED):
            return timezone.now() > self.due_date
        return False

    def complete(self) -> None:
        """Отметить задачу выполненной."""
        self.status = self.Status.DONE
        self.save(update_fields=["status", "updated_at"])

    def cancel(self) -> None:
        """Отменить задачу."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])

    @classmethod
    def get_active_for_user(cls, user):
        """Получить все активные задачи пользователя."""
        return cls.objects.filter(
            owner=user,
            status__in=[cls.Status.TODO, cls.Status.IN_PROGRESS],
        )

    @classmethod
    def get_statistics(cls, user) -> dict:
        """Статистика задач пользователя."""
        tasks = cls.objects.filter(owner=user)
        total = tasks.count()
        done = tasks.filter(status=cls.Status.DONE).count()
        return {
            "total": total,
            "done": done,
            "active": tasks.filter(
                status__in=[cls.Status.TODO, cls.Status.IN_PROGRESS]
            ).count(),
            "cancelled": tasks.filter(status=cls.Status.CANCELLED).count(),
            "completion_rate": round(done / total * 100, 1) if total > 0 else 0.0,
        }
