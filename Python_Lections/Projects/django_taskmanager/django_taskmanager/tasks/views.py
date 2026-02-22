from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.http import JsonResponse
from django.contrib import messages

from .models import Task
from .forms import TaskForm, TaskFilterForm
from .services import TaskService


class TaskListView(LoginRequiredMixin, generic.ListView):
    """Список задач текущего пользователя."""

    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self):
        form = TaskFilterForm(self.request.GET)
        qs = Task.objects.filter(owner=self.request.user)

        if form.is_valid():
            cd = form.cleaned_data
            qs = TaskService.filter_tasks(
                user=self.request.user,
                status=cd.get("status"),
                priority=cd.get("priority"),
                category=cd.get("category"),
                search=cd.get("search"),
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = TaskFilterForm(self.request.GET)
        ctx["stats"] = Task.get_statistics(self.request.user)
        return ctx


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    """Детальная страница задачи."""

    model = Task
    template_name = "tasks/task_detail.html"

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    """Создание задачи."""

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Задача создана!")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Редактирование задачи."""

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = "/"

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Задача обновлена!")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Удаление задачи."""

    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = "/"

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


@login_required
def task_complete(request, pk):
    """Быстрое завершение задачи."""
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.complete()
    messages.success(request, f'Задача "{task.title}" выполнена!')
    return redirect("task-list")


@login_required
def dashboard(request):
    """Дашборд со статистикой."""
    stats = Task.get_statistics(request.user)
    overdue = TaskService.get_overdue_tasks(request.user)
    return render(request, "tasks/dashboard.html", {
        "stats": stats,
        "overdue_tasks": overdue,
    })


@login_required
def api_task_stats(request):
    """API endpoint — статистика в JSON."""
    stats = Task.get_statistics(request.user)
    return JsonResponse(stats)
