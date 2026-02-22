from django import forms
from .models import Task, Category


class TaskForm(forms.ModelForm):
    """Форма создания/редактирования задачи."""

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "status", "category", "due_date"]
        widgets = {
            "due_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if len(title) < 3:
            raise forms.ValidationError("Заголовок должен содержать минимум 3 символа.")
        return title


class TaskFilterForm(forms.Form):
    """Форма фильтрации задач."""

    STATUS_CHOICES = [("", "Все статусы")] + list(Task.Status.choices)
    PRIORITY_CHOICES = [("", "Все приоритеты")] + list(Task.Priority.choices)

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Все категории",
    )
    search = forms.CharField(required=False, max_length=100)


class CategoryForm(forms.ModelForm):
    """Форма категории."""

    class Meta:
        model = Category
        fields = ["name", "slug", "description"]
