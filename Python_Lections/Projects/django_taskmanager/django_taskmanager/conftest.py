"""Корневой conftest — гарантирует настройку Django ДО загрузки тестов."""
import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

if not settings.configured:
    django.setup()


import pytest


@pytest.fixture(autouse=True)
def _enable_db_access_for_all_tests(db):
    """
    Автоматически даёт доступ к тестовой БД всем тестам.
    pytest-django по умолчанию блокирует доступ к БД без явного маркера —
    эта фикстура снимает это ограничение глобально.
    """
    pass
