# Task Manager — Django + Pytest

Тестовый проект на Django с полным покрытием юнит-тестами на pytest.

## Структура проекта

```
django_taskmanager/
├── manage.py
├── pytest.ini                  # Конфигурация pytest + coverage
├── requirements.txt
├── taskmanager/                # Настройки Django-проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks/                      # Приложение «Задачи»
│   ├── models.py               # Task, Category
│   ├── forms.py                # TaskForm, TaskFilterForm, CategoryForm
│   ├── services.py             # TaskService, CategoryService (бизнес-логика)
│   ├── views.py                # CBV + FBV
│   ├── urls.py
│   └── admin.py
├── templates/                  # HTML-шаблоны
└── tests/                      # Тесты
    ├── conftest.py             # Фикстуры + Factory Boy фабрики
    ├── test_models.py          # Тесты моделей
    ├── test_forms.py           # Тесты форм
    ├── test_services.py        # Тесты сервисного слоя
    ├── test_views.py           # Тесты представлений (views)
    └── test_urls.py            # Тесты маршрутизации
```

## Быстрый старт

```bash
cd django_taskmanager

# Виртуальное окружение
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# Зависимости
pip install -r requirements.txt

# ⚠️ ВАЖНО: сначала создать миграции и применить их
python manage.py makemigrations tasks
python manage.py migrate

# Запуск тестов с покрытием
pytest

# Только конкретный файл
pytest tests/test_models.py -v

# С HTML-отчётом о покрытии
pytest --cov-report=html
open htmlcov/index.html
```

## Что покрыто тестами

| Модуль           | Что тестируется                                                       |
|------------------|-----------------------------------------------------------------------|
| `test_models.py` | Создание, `__str__`, `is_overdue`, `complete()`, `cancel()`, статистика |
| `test_forms.py`  | Валидация полей, очистка данных, обработка дубликатов                  |
| `test_services.py` | Фильтрация, массовое завершение, просроченные, категории с подсчётом |
| `test_views.py`  | Аутентификация, CRUD, изоляция данных, пагинация, JSON API            |
| `test_urls.py`   | Маршруты → view-классы, проверка URL-путей                            |

## Используемые инструменты

- **pytest-django** — интеграция pytest с Django
- **pytest-cov** — покрытие кода (coverage)
- **factory-boy** — фабрики тестовых данных вместо ручных фикстур
- **parametrize** — параметризованные тесты для проверки множества кейсов
