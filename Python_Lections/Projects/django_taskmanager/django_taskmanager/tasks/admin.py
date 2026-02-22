from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "priority", "category", "due_date", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description")
    raw_id_fields = ("owner",)
