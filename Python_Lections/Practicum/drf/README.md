View-классы API
Следующий этап работы с Views в Django REST framework — встроенные view-классы. У них множество преимуществ перед view-функциями:

    возможность применять готовый код для решения стандартных задач;
    наследование, которое позволяет повторно использовать уже написанный код.

Встроенные классы DRF можно условно разделить на низкоуровневые и высокоуровневые. Низкоуровневые содержат лишь базовую структуру класса, его скелет, разработчик сам должен описать работу класса. Их применяют для решения нестандартных задач.
Типовые задачи (скажем, CRUD) удобнее решать с помощью высокоуровневых view-классов: в них уже заготовлены все инструменты для решения стандартных задач.
Низкоуровневые view-классы в DRF
Начнём с низкоуровневого view-класса APIView из модуля rest_framework.views. 
Если view-класс унаследован от класса APIView, то при получении GET-запроса в классе будет вызван метод get(), а при получении POST-запроса — метод post(). Такие методы описаны для всех типов запросов, но по умолчанию эти методы не выполняют никаких действий, их нужно описывать самостоятельно.

# Скелет есть, а кода нет. Надо самостоятельно описать необходимые методы.
class MyAPIView(APIView):
    def get(self, request):
        ...

    def post(self, request):
        ...

    def put(self, request):
        ...

    def patch(self, request):
        ...

    def delete(self, request):
        ... 

В целом этот класс работает так же, как и view-функции. 
Практика: редактируем вместе
Измените проект Kittygram: вместо view-функции опишите view-класс.
Импортируйте класс APIView из rest_framework.views, создайте класс-наследник и переопределите в нём методы get() и post(). Код почти ничем не будет отличаться от того, что был во view-функции, но будет написан в объектно-ориентированном стиле.

# Обновлённый views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cat
from .serializers import CatSerializer


class APICat(APIView):
    def get(self, request):
        cats = Cat.objects.all()
        serializer = CatSerializer(cats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

Чтобы всё заработало, исправьте код в urls.py, ведь синтаксис вызова view-классов отличается от синтаксиса вызова view-функций.

# urls.py
from django.urls import path

from cats.views import APICat

urlpatterns = [
    path('cats/', APICat.as_view()),
] 

Как и при работе со view-функциями, все операции CRUD при использовании view-классов принято разделять на 2 группы: в одном view-классе описывается создание нового объекта и запрос всех объектов (например класс APICat), а в другом классе — получение/изменение/удаление определённого объекта (например класс APICatDetail).
Внесите изменения в Kittygram, запустите проект и поработайте с запросами через Postman: API будет работать так же, как и со view-функциями.
Generic Views: высокоуровневые view-классы
Для типовых действий, например, для вывода списка объектов или для запроса объекта по id удобнее использовать высокоуровневые view-классы, «дженерики» (англ. Generic Views): в них уже реализованы все механизмы, необходимые для решения задачи.
Некоторые из Generic Views выполняют строго определённую задачу (например, обрабатывают только один тип запросов), другие — более универсальны и могут «переключаться» на разные задачи в зависимости от HTTP-метода, которым был отправлен запрос. 
В дженериках задают всего два поля: queryset (набор записей, который будет обрабатываться в классе) и serializer_class (сериализатор, который будет преобразовывать объекты в формат JSON). В DRF все Generic Views объединены в модуле rest_framework.generics. Полный список можно посмотреть в документации DRF.
Рефакторинг кода: пишем Kittygram на Generic Views
Операции, описанные во view-классе проекта Kittygram, типичны для любого API. Есть смысл переписать код, заменив низкоуровневый view-класс на дженерики.
Для работы возьмём два класса и на них реализуем все шесть операций классического API:

    комбинированный класс ListCreateAPIView: он возвращает всю коллекцию объектов (например, всех котиков) или может создать новую запись в БД;
    комбинированный класс RetrieveUpdateDestroyAPIView: его работа — возвращать, обновлять или удалять объекты модели по одному.

    Это практическая работа: вносите изменения, описанные в этом уроке, в проект Kittygram, развёрнутый на вашем компьютере.

Импортируйте в код всё необходимое: generics из rest_framework, модель и сериализатор. Затем опишите дженерики:

# Обновлённый views.py
from rest_framework import generics

from .models import Cat
from .serializers import CatSerializer


class CatList(generics.ListCreateAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer


class CatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer 

Измените вызов view-класса в urls.py:

# Обновлённый urls.py
from django.urls import path

from cats.views import CatList, CatDetail

urlpatterns = [
    path('cats/', CatList.as_view()),
    path('cats/<int:pk>/', CatDetail.as_view()),
] 

Теперь проект Kittygram поддерживает весь API CRUD для модели Cat (а не только получение списка всех котиков и добавление нового котика). При минимальном количестве изменений в коде мы сделали API для модели Cat в Kittygram! Да и кода стало меньше. А где меньше кода, там меньше ошибок.
В коде явным образом не описана обработка разных типов запросов: всё происходит «под капотом» view-классов. Внесите изменения в свой локальный проект Kittygram и отправьте запросы разного типа через Postman: убедитесь в работоспособности проекта.
Специализированные Generic Views
В коде Kittygram view-классы унаследованы от комбинированных дженериков: они выполняют все операции CRUD. Для решения нашей задачи именно комбинированные дженерики подходят лучше всего. Но в некоторых случаях применение комбинированных view-классов будет избыточным или даже опасным. 
Например, при создании API «только для чтения» (как знакомый вам StarWarsAPI) лучше подключить специализированный ListAPIView, который выполняет ровно одно действие: выводит список объектов в ответ на GET-запрос. Это лучше и с точки зрения безопасности, и с точки зрения отсутствия избыточного кода.
Есть ещё несколько специализированных view-классов DRF:

    RetrieveAPIView — возвращает один объект (обрабатывает только GET-запросы);
    CreateAPIView — создаёт новый объект (обрабатывает только POST-запросы);
    UpdateAPIView — изменяет объект (обрабатывает только PUT- и PATCH-запросы);
    DestroyAPIView — удаляет объект (обрабатывает только DELETE-запросы).

Эти классы описываются в коде точно так же, как и комбинированные view-классы модуля rest_framework.generics.
Что в итоге
Работа с view-классами в DRF отличается от работы с привычными view-классами в Django только сериализацией и отсутствием HTML-шаблонов.
Удобная шпаргалка по классам DRF. Добавьте эту страницу в закладки и заглядывайте туда регулярно: с каждым разом этот справочник будет становиться всё понятнее и полезнее.## Краткий конспект: Проектирование REST API

Проектирование API — это фундамент, влияющий на удобство и долговечность сервиса. Два главных принципа: **консистентность** и **расширяемость**.

### 1. Консистентность (Согласованность)

Это единообразие форматов данных во всем API.

*   **Целостность данных:** Информация об одном и том же объекте должна быть идентичной при запросе через разные эндпоинты.
*   **Единый формат типов данных:** Если для даты выбран формат `unix-timestamp`, он должен использоваться везде, где фигурирует дата, а не заменяться на строку в одном из ответов.

**Пример нарушения консистентности:**
Модель `Post` содержит дату.
```python
# models.py
class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
```

*   **Запрос поста:** `GET /api/v1/posts/10/`
    *   **Ответ (Unix-timestamp):** `[[10, "Текст", 1618567801, 1]]` (дата - число)
*   **Запрос комментария:** `GET /api/v1/posts/10/comments/1/`
    *   **Ответ (Строка - НЕПРАВИЛЬНО):** `[[1, "Коммент", "2020-03-23T18:02:33Z", 10]]` (дата - строка)
    *   **Ответ (Unix-timestamp - ПРАВИЛЬНО):** `[[1, "Коммент", 1618565516, 10]]` (дата снова число)

### 2. Расширяемость

Возможность добавлять новые данные в ответ API, не ломая существующие клиентские приложения.

**Проблема нерасширяемого подхода:**
Изначально API возвращает список (массив) значений.

```json
# Ответ: [id, text, pub_date, author_id]
[10, "Это текст моего поста.", 1618567801, 1]
```
Если позже потребуется добавить `group_id`, структура сломается. Старые клиенты будут ожидать дату на позиции индекса `2`, а получат `group_id`.

**Решение: Использовать объекты (словари) вместо списков**

*   **Уровень 1:** Возвращать данные в формате `{"ключ": "значение"}`. Добавление нового поля (`group_id`) не сломает старых клиентов, так как они обращаются к данным по ключам.

```json
[{
    "id": 10,
    "text": "Это текст моего поста.",
    "pub_date": 1618567801,
    "author_id": 1,
    "group_id": 7
}]
```

*   **Уровень 2 (Лучшая практика):** Группировать данные по смыслу и предусмотреть место для будущих мета-данных. Выделите основной объект и дополнительные блоки (например, `links`).

```json
[{
    "post": {
        "id": 10,
        "text": "Это текст моего поста.",
        "pub_date": 1618567801,
        "author_id": 1,
        "group_id": 7
    },
    "links": {
        "similar_posts": ["/posts/12", "/posts/23"],
        "comments_url": "/posts/10/comments/"
    }
}]
```
Такой подход позволяет расширять ответ любыми данными, даже не связанными напрямую с моделью, без риска для существующей структуры.

### Главный вывод

*   **Консистентность:** Договорись о форматах (даты, координаты, ключи) и придерживайся их во всем API.
*   **Расширяемость:** Не используй списки для сложных данных. Используй объекты (`{}`). Проектируй ответ с запасом (например, вложенные объекты `data` или `links`), чтобы будущие изменения были безопасными.

## Краткий конспект: Инструменты тестирования API

Для отправки запросов к API существуют специализированные инструменты, которые делятся на три категории: консольные, встраиваемые и графические.

### 1. Классификация инструментов

*   **Консольные** (curl, httpie): Управление через командную строку.
*   **Встраиваемые** (REST Client для VS Code): Плагины для редакторов кода, работа без переключения между приложениями.
*   **Графические** (Postman): Самостоятельные программы с собственным интерфейсом.

### 2. httpie (консольный клиент)

Консольный инструмент для отправки HTTP-запросов. Можно протестировать в веб-эмуляторе.

**Пример запроса и ответа:**
```
PUT /put HTTP/1.1
API-Key: foo
...
{
    "hello": "world"
}

HTTP/1.1 200 OK
...
{
    "args": {},
    "data": "{\"hello\": \"world\"}",
    "json": {
        "hello": "world"
    },
    "url": "http://pie.dev/put"
}
```

### 3. REST Client (плагин для VS Code)

Встраиваемый инструмент для работы с запросами прямо из редактора кода.

**Установка:**
Через панель расширений VS Code найти "REST Client" → Install.

**Формат файла запросов (.http):**

```http
# Пример GET запроса
GET https://jsonplaceholder.typicode.com/posts/1

###

# Пример POST запроса
POST https://jsonplaceholder.typicode.com/posts
Content-Type: application/json

{
    "title": "My Title",
    "body": "My text",
    "userId": 1
}
```

**Особенности:**
- Запросы разделяются строкой с `###`.
- Для отправки нажать ссылку "SendRequest" над запросом.
- Файл можно сохранить в репозитории для команды.

### 4. Postman (графический клиент)

Самый популярный инструмент с богатой функциональностью.

**Установка и настройка:**
1. Скачать с официального сайта (браузерная версия не работает с `127.0.0.1`).
2. Авторизоваться для сохранения данных в облаке.
3. Использовать **Workspace** (рабочее окружение) для разделения проектов.

**Интерфейс:**
- Левая панель — сохраненные запросы и история.
- Правая панель — создание и настройка запросов.
- Кнопка "+" для создания нового запроса.

**Настройка запроса:**
- Метод (GET, POST, PUT, DELETE и др.)
- URL
- Параметры (Params)
- Заголовки (Headers)
- Тело запроса (Body)

**Пример GET-запроса к GitHub API:**
```
GET https://api.github.com/users/yandex-praktikum
```

**Пример ответа:**
```json
{
    "login": "yandex-praktikum",
    "id": 58176914,
    "public_repos": 6,
    "followers": 90,
    "created_at": "2019-11-25T13:38:59Z",
    "updated_at": "2021-03-24T16:15:56Z"
    // ... другие поля
}
```

### 5. Рекомендации

*   Не нужно устанавливать все инструменты сразу — выберите один понравившийся.
*   В курсе примеры будут показаны в **Postman**, но вы можете работать в любом инструменте.
*   Внимательно изучайте ответы API: структуру JSON, вложенность, именование полей — это поможет в проектировании собственного API.


### Краткий конспект: Сериализаторы в DRF

### 1. Отличия интерфейсов для людей и программ

**Для людей (веб-страницы):**
- Данные из БД встраиваются в HTML-шаблоны через `render`.
- Результат — HTML-страница для чтения человеком.

**Для программ (API):**
- Нужен единый формат обмена (JSON, XML).
- Программы могут быть на разных языках, поэтому данные постоянно преобразуются.

### 2. Сериализация и десериализация

**Сериализация** — преобразование сложных Python-объектов (экземпляры моделей, queryset) в простые типы данных Python, а затем в JSON для отправки клиенту.

**Пример сериализации:**
```python
# Объект модели Post
post = Post(
    id=87,
    author='Робинзон Крузо', 
    text='23 ноября. Закончил работу над лопатой и корытом.',
    pub_date='1659-11-23T18:02:33.123543Z'
)

# Результат сериализации в JSON
{
    "id": 87,
    "author": "Робинзон Крузо", 
    "text": "23 ноября. Закончил работу над лопатой и корытом.",
    "pub_date": "1659-11-23T18:02:33.123543Z"
}
```

**Десериализация** — обратный процесс: преобразование JSON из запроса в Python-объекты с обязательной **валидацией** данных.

**Этапы десериализации:**
1. Преобразование JSON в простые типы Python
2. Валидация (проверка соответствия ожиданиям)
3. Конвертация валидированных данных в сложные объекты (модели)

**Пример входного JSON для создания поста:**
```json
{
    "author": "Робинзон Крузо", 
    "text": "24 декабря. Всю ночь и весь день шёл проливной дождь.",
    "pub_date": "1659-12-24T21:14:56.123543Z"
}
```

### 3. Сериализаторы (Serializers) в DRF

Классы, отвечающие за все три операции: **сериализацию**, **валидацию** и **десериализацию**.

**Два основных типа:**
- `Serializer` — для работы с обычными Python-классами
- `ModelSerializer` — для работы с моделями Django

**Обязательные компоненты сериализатора:**
- **Поля** — названия полей (ключи в JSON)
- **Типы полей** — для правильной конвертации
- **Параметры полей** — ограничения (max_length и т.д.)

### 4. ModelSerializer (для моделей)

Самый часто используемый тип. Автоматически определяет поля и их типы на основе модели.

**Структура файла `serializers.py`:**
```python
from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # Явное перечисление полей (рекомендуется)
        fields = ('id', 'post', 'author', 'text', 'created')
        
        # Или все поля модели:
        # fields = '__all__'
        
        # Или все, кроме указанных:
        # exclude = ('field_to_hide',)
```

**Важно:** Лучше явно перечислять поля, чем использовать `__all__`, чтобы случайно не опубликовать новые поля, добавленные в модель позже.

### 5. Serializer (для обычных классов)

Требует явного описания всех полей.

```python
# Обычный Python-класс
class Book():
    def __init__(self, author, title, pub_year, genre):
        self.author = author
        self.title = title
        self.pub_year = pub_year
        self.genre = genre

# Сериализатор для него
class BookSerializer(serializers.Serializer):
    # Явно описываем поля, типы и параметры
    author = serializers.CharField(max_length=256)
    title = serializers.CharField(max_length=512)
    pub_year = serializers.IntegerField()
    genre = serializers.CharField(max_length=64)  # исправлено: max_length, а не просто 64
```

**Важно:**
- Имена полей в сериализаторе должны совпадать с именами атрибутов класса
- Эти же имена станут ключами в JSON

### 6. Универсальность сериализаторов

**Один сериализатор — два режима работы:**

```python
# Режим СЕРИАЛИЗАЦИИ (объект -> JSON)
post = Post.objects.get(id=1)
serializer = CommentSerializer(post)  # Передали объект
json_data = serializer.data  # Получили словарь для рендеринга в JSON

# Режим ДЕСЕРИАЛИЗАЦИИ (JSON -> объект)
data = {
    "author": "Робинзон Крузо",
    "text": "Новый пост",
    "pub_date": "1659-12-24T21:14:56.123543Z"
}
serializer = CommentSerializer(data=data)  # Передали данные
if serializer.is_valid():  # Валидация
    new_comment = serializer.save()  # Создание объекта
```

### 7. Структура проекта

Код сериализаторов принято выносить в отдельный файл:
```
your_app/
    ├── models.py
    ├── serializers.py    # <-- Здесь живут сериализаторы
    ├── views.py
    └── urls.py
```

## Краткий конспект: View-функции API в DRF

### 1. Что такое view-функция API?

**View-функция** в DRF — это Python-функция, которая обрабатывает HTTP-запросы к API и возвращает HTTP-ответ (обычно в JSON).

**Отличие от обычных Django view:**
- Вместо HTML возвращают JSON
- Используют декоратор `@api_view`
- Возвращают объект `Response` вместо `HttpResponse`

### 2. Декоратор @api_view (ОБЯЗАТЕЛЕН!)

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])  # Разрешенные методы
def hello(request):
    return Response({'message': 'Привет, API!'})
```

**Что делает декоратор:**
- Настраивает view для работы с API
- Автоматически обрабатывает неподдерживаемые методы (возвращает 405)
- Добавляет в `request` объект `request.data` (содержит данные из запроса)

### 3. request.data — доступ к данным запроса

```python
@api_view(['POST'])
def create_cat(request):
    # request.data содержит данные из тела запроса (JSON, form-data и т.д.)
    cat_name = request.data.get('name')
    cat_color = request.data.get('color')
    
    return Response({
        'message': f'Создан котик {cat_name} цвета {cat_color}',
        'received_data': request.data  # все полученные данные
    })
```

**Важно:** `request.data` работает для всех типов запросов (POST, PUT, PATCH) и автоматически парсит JSON.

### 4. Валидация данных через сериализатор

**Главное правило:** Данные из запроса НИКОГДА не используются напрямую! Они всегда проходят через сериализатор для валидации.

```python
from .serializers import CatSerializer

@api_view(['POST'])
def create_cat(request):
    # Передаем данные из запроса в сериализатор
    serializer = CatSerializer(data=request.data)
    
    # ВАЛИДАЦИЯ: проверяем, соответствуют ли данные модели
    if serializer.is_valid():
        # Если данные валидны - сохраняем в БД
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        # Если данные невалидны - возвращаем ошибки
        return Response(serializer.errors, status=400)
```

### 5. Что происходит при валидации?

`serializer.is_valid()` проверяет:
- Все ли обязательные поля присутствуют
- Правильные ли типы данных (текст, число, дата)
- Соответствуют ли ограничения (max_length, min_value и т.д.)
- Выполняются ли кастомные валидаторы

### 6. Два режима работы сериализатора

```python
# Режим 1: ДЕСЕРИАЛИЗАЦИЯ (JSON -> объект) - для создания/обновления
serializer = CatSerializer(data=request.data)  # только data

# Режим 2: СЕРИАЛИЗАЦИЯ (объект -> JSON) - для ответов
cat = Cat.objects.get(id=1)
serializer = CatSerializer(cat)  # только объект
```

### 7. Обработка разных HTTP-методов

```python
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def handle_cats(request):
    if request.method == 'GET':
        # Получение данных (сериализация)
        cats = Cat.objects.all()
        serializer = CatSerializer(cats, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Создание (десериализация + валидация)
        serializer = CatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'PUT':
        # Полное обновление
        cat = Cat.objects.get(id=request.data.get('id'))
        serializer = CatSerializer(cat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
```

### 8. Важные параметры сериализатора

```python
# Для работы со списком объектов (many=True)
serializer = CatSerializer(data=request.data, many=True)  # ожидает список

# Для частичного обновления (partial=True)
serializer = CatSerializer(cat, data=request.data, partial=True)  # не все поля обязательны
```

### 9. Итог: что делает view-функция API?

1. **Принимает HTTP-запрос** (GET, POST, PUT, PATCH, DELETE)
2. **Извлекает данные** из `request.data` (для POST/PUT/PATCH)
3. **Передает данные в сериализатор** для валидации
4. **Проверяет результат валидации** (`is_valid()`)
5. **Выполняет действие** (сохраняет в БД, удаляет, обновляет)
6. **Возвращает Response** с данными или ошибками

## Что указывается в скобках при вызове сериализатора

При создании экземпляра сериализатора в скобках передаются аргументы, которые определяют **режим работы** сериализатора и **данные**, с которыми он будет работать.

### 1. Основные комбинации аргументов

#### А. Для СЕРИАЛИЗАЦИИ (объект → JSON)
```python
# Получение одного объекта
serializer = CatSerializer(cat)

# Получение списка объектов
serializer = CatSerializer(cats, many=True)
```
- **Первый аргумент**: объект модели или queryset
- **`many=True`**: обязателен для списков

#### Б. Для ДЕСЕРИАЛИЗАЦИИ (JSON → объект) — создание
```python
# Создание одного объекта
serializer = CatSerializer(data=request.data)

# Создание нескольких объектов
serializer = CatSerializer(data=request.data, many=True)
```
- **`data=`**: данные из запроса (словарь или список)

#### В. Для ДЕСЕРИАЛИЗАЦИИ — обновление
```python
# Полное обновление (PUT)
serializer = CatSerializer(cat, data=request.data)

# Частичное обновление (PATCH)
serializer = CatSerializer(cat, data=request.data, partial=True)
```
- **Первый аргумент**: существующий объект
- **`data=`**: новые данные
- **`partial=True`**: разрешает отсутствие обязательных полей

### 2. Полный список возможных аргументов

| Аргумент | Что означает | Когда использовать |
|----------|--------------|-------------------|
| `instance` | Объект для сериализации | Можно передавать первым аргументом (без ключа) |
| `data` | Данные для десериализации | POST, PUT, PATCH запросы |
| `many=True` | Работа со списком объектов | Для queryset или списка данных |
| `partial=True` | Частичное обновление | PATCH-запросы |
| `context` | Дополнительный контекст | Когда нужны request, view и т.д. |
| `read_only` | Только для чтения | Редко, обычно в Meta-классе |

### 3. Примеры всех вариантов

```python
# 1. Сериализация одного объекта
cat = Cat.objects.get(id=1)
serializer = CatSerializer(cat)

# 2. Сериализация списка объектов
cats = Cat.objects.all()
serializer = CatSerializer(cats, many=True)

# 3. Создание нового объекта
serializer = CatSerializer(data=request.data)

# 4. Создание нескольких объектов
serializer = CatSerializer(data=request.data, many=True)

# 5. Полное обновление объекта
cat = Cat.objects.get(id=1)
serializer = CatSerializer(cat, data=request.data)

# 6. Частичное обновление объекта
cat = Cat.objects.get(id=1)
serializer = CatSerializer(cat, data=request.data, partial=True)

# 7. С контекстом (передаем request в сериализатор)
serializer = CatSerializer(cat, context={'request': request})
```

### 4. Что такое `context`?

`context` позволяет передавать в сериализатор дополнительную информацию:

```python
# Передаем request в сериализатор
serializer = CatSerializer(cat, context={'request': request})

# В сериализаторе можно получить:
request = self.context.get('request')
user = request.user  # доступ к текущему пользователю
```

### 5. Таблица соответствия HTTP-методов и аргументов

| HTTP-метод | Действие | Аргументы сериализатора |
|------------|----------|------------------------|
| **GET** (один объект) | Получить | `CatSerializer(cat)` |
| **GET** (список) | Получить все | `CatSerializer(cats, many=True)` |
| **POST** (один) | Создать | `CatSerializer(data=request.data)` |
| **POST** (список) | Создать несколько | `CatSerializer(data=request.data, many=True)` |
| **PUT** | Полностью обновить | `CatSerializer(cat, data=request.data)` |
| **PATCH** | Частично обновить | `CatSerializer(cat, data=request.data, partial=True)` |
| **DELETE** | Удалить | Сериализатор не нужен |

### 6. Коротко: что куда писать?

- **Если работаем с объектом из БД** → передаем его первым аргументом
- **Если работаем с данными из запроса** → передаем их через `data=`
- **Если работаем со списком** → добавляем `many=True`
- **Если это PATCH-запрос** → добавляем `partial=True`
- **Если в сериализаторе нужен request или пользователь** → передаем `context`


### Пример написанного кода 
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404  # добавили импорт
from .models import Post
from .serializers import PostSerializer


@api_view(['GET', 'POST'])
def api_posts(request):
    if request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # GET-запрос
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_posts_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

## Краткий конспект: View-классы в DRF

### 1. Преимущества view-классов перед view-функциями

- **Готовый код** для стандартных задач
- **Наследование** — повторное использование кода
- Разделение на низкоуровневые и высокоуровневые классы

### 2. Низкоуровневые view-классы: APIView

Базовый класс из `rest_framework.views`. Требует ручной реализации методов.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class APICat(APIView):
    def get(self, request):
        cats = Cat.objects.all()
        serializer = CatSerializer(cats, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**Маршрутизация:**
```python
urlpatterns = [
    path('cats/', APICat.as_view()),  # .as_view() обязательно для классов
]
```

**Важно:** Для CRUD обычно используют два класса:
- Один для списка и создания (`GET` всех объектов + `POST`)
- Второй для работы с конкретным объектом (`GET`, `PUT`, `PATCH`, `DELETE`)

### 3. Высокоуровневые view-классы (Generic Views)

Находятся в модуле `rest_framework.generics`. Требуют определения всего двух полей:
- `queryset` — набор записей для обработки
- `serializer_class` — сериализатор для преобразования

#### Комбинированные дженерики (CRUD)

```python
from rest_framework import generics

class CatList(generics.ListCreateAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

class CatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
```

**Маршрутизация:**
```python
urlpatterns = [
    path('cats/', CatList.as_view()),
    path('cats/<int:pk>/', CatDetail.as_view()),
]
```

**Что дают эти классы:**
- `ListCreateAPIView` → `GET` (список) + `POST` (создание)
- `RetrieveUpdateDestroyAPIView` → `GET` (один объект) + `PUT`/`PATCH` + `DELETE`

### 4. Специализированные Generic Views

Для задач, где не нужен полный CRUD:

| Класс | HTTP-методы | Назначение |
|-------|-------------|------------|
| `ListAPIView` | `GET` | Только список объектов |
| `RetrieveAPIView` | `GET` | Только один объект |
| `CreateAPIView` | `POST` | Только создание |
| `UpdateAPIView` | `PUT`, `PATCH` | Только обновление |
| `DestroyAPIView` | `DELETE` | Только удаление |

**Пример для read-only API:**
```python
class CatReadOnlyList(generics.ListAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

class CatReadOnlyDetail(generics.RetrieveAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
```

### 5. Структура проекта после рефакторинга

```
cats/
├── models.py          # Модель Cat
├── serializers.py     # CatSerializer
├── views.py           # View-классы (APIView или generics)
└── urls.py            # Маршруты с .as_view()
```

### 6. Ключевые отличия от обычных Django views

- Вместо HTML-шаблонов — **сериализация** в JSON
- Вместо `render()` — возврат `Response()` или `JsonResponse()`
- Встроенная поддержка всех HTTP-методов
- Минимум кода для типовых операций

### 7. Полезные ссылки

- [Документация DRF по Generic Views](https://www.django-rest-framework.org/api-guide/generic-views/)
- [Справочник по классам DRF](https://www.cdrf.co/) — добавить в закладки


###Пример написанных view-классов 
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer
# Импортируйте в код всё необходимое
from django.shortcuts import get_object_or_404


class APIPost(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class APIPostDetail(APIView):
    
    def get(self, request,pk):
        post = get_object_or_404(Post, id=pk)
        posts = Post.objects.all()
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request,pk):
        post = get_object_or_404(Post, id=pk)
        serializer = PostSerializer(post,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request,pk):
        post = get_object_or_404(Post, id=pk)
        serializer = PostSerializer(post,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,pk):
        post = get_object_or_404(Post, id=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```
