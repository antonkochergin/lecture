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


### Пример написанных view-классов 
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
### С дженериками 
```python
#  Импортируйте в код всё необходимое
from .models import Post
from .serializers import PostSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class APIPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class APIPostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

### Супер-шпора Яндекса 
https://code.s3.yandex.net/Python-dev/cheatsheets/043-drf-serializatsija-viewset-routery-shpora/043-drf-serializatsija-viewset-routery-shpora.html

### ViewSets (Наборы представлений)

Высокоуровневые view-классы, реализующие все операции CRUD в одном классе.

#### ModelViewSet (универсальный)
```python
from rest_framework import viewsets
from .models import Cat
from .serializers import CatSerializer

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
```

**Что дает:**
- GET (список) + POST → `/cats/`
- GET (один объект) + PUT/PATCH/DELETE → `/cats/<int:pk>/`
- Все 6 CRUD операций из коробки

#### ReadOnlyModelViewSet (только чтение)
```python
class CatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
```

**Что дает:**
- Только GET-запросы (список и один объект)
- Без возможности создания/изменения/удаления

### 2. Routers (Роутеры)

Автоматически создают эндпоинты для ViewSets.

#### SimpleRouter
```python
# urls.py
from rest_framework.routers import SimpleRouter
from django.urls import include, path
from .views import CatViewSet

router = SimpleRouter()
router.register('cats', CatViewSet)  # регистрация вьюсета

urlpatterns = [
    path('', include(router.urls)),  # все эндпоинты из роутера
]
```

**Создает эндпоинты:**
- `cats/` → для списка и создания
- `cats/<int:pk>/` → для одного объекта

#### DefaultRouter (рекомендуемый)
```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('cats', CatViewSet)
```

**Дополнительно создает:**
- Корневой эндпоинт `/` → список всех доступных ресурсов API
- name='api-root' для корневого эндпоинта

### 3. Параметр name в эндпоинтах

Роутеры автоматически создают name для эндпоинтов:
- `'cat-list'` → для работы с коллекцией
- `'cat-detail'` → для работы с конкретным объектом

### 4. Параметр basename

Нужен, когда queryset задан не явно, а через `get_queryset()`:

```python
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        cat_id = self.kwargs.get("cat_id")
        return Comment.objects.filter(cat=cat_id)
```

Регистрация с обязательным basename:
```python
router.register('comments', CommentViewSet, basename='comment')
```

Можно переопределить basename:
```python
router.register('cats', CatViewSet, basename='tiger')
# Результат: tiger-list, tiger-detail вместо cat-list, cat-detail
```

### 5. Сравнение подходов

| Подход | Классы | Эндпоинты | Код |
|--------|--------|-----------|-----|
| **APIView** | 2 класса (List, Detail) | Прописываем вручную | Много |
| **Generic Views** | 2 класса (List, Detail) | Прописываем вручную | Средне |
| **ViewSet + Router** | 1 класс | Автоматически | Минимум |

### 6. Полный пример с DefaultRouter

**views.py:**
```python
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

**urls.py:**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

### 7. Преимущества ViewSets + Routers

✅ **Минимум кода** — один класс вместо двух
✅ **Автоматические URL** — не нужно прописывать вручную
✅ **Стандартизация** — единый подход для всех ресурсов
✅ **Корневой эндпоинт** (в DefaultRouter) — документация API
✅ **Меньше ошибок** — меньше кода для написания

### 8. Шпаргалка (сохранить в закладки)

- [Документация DRF по ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Документация по Routers](https://www.django-rest-framework.org/api-guide/routers/)
- [Справочник CDRF](https://www.cdrf.co/)


### Сериализаторы для связанных моделей

### 1. Связи между моделями

```python
# models.py
class Owner(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    birth_year = models.IntegerField()
    # Связь "один-ко-многим" (ForeignKey)
    owner = models.ForeignKey(
        Owner, related_name='cats', on_delete=models.CASCADE)
    # Связь "многие-ко-многим" (ManyToManyField)
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')
```

### 2. Базовые сериализаторы

```python
# serializers.py
class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ('first_name', 'last_name')

class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year')
```

### 3. Типы полей для связанных моделей

#### PrimaryKeyRelatedField (по умолчанию)
```python
# В ответе будут id связанных объектов
[
    {
        "first_name": "Theodor",
        "last_name": "Voland",
        "cats": [1, 2]  # id котиков
    }
]
```

#### StringRelatedField (строковое представление)
```python
class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')

# Результат: вместо id - строковое представление (из __str__)
{
    "first_name": "Theodor",
    "last_name": "Voland",
    "cats": ["Барсик", "Мурзик"]  # name из __str__
}
```

**Важно:**
- `many=True` — для связи "один-ко-многим" (у одного хозяина много котов)
- `read_only=True` — StringRelatedField не поддерживает запись

### 4. Вложенные сериализаторы

Для получения полных объектов связанной модели, а не только id или строк:

```python
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name')

class CatSerializer(serializers.ModelSerializer):
    # Вложенный сериализатор
    achievements = AchievementSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements')
```

**Результат:**
```json
{
    "id": 1,
    "name": "Барсик",
    "color": "White",
    "birth_year": 2017,
    "owner": "Theodor Voland",
    "achievements": [
        {"id": 1, "name": "поймал мышку"},
        {"id": 2, "name": "разбил вазу"}
    ]
}
```

### 5. Запись данных с вложенными сериализаторами

По умолчанию вложенные сериализаторы **только для чтения**. Чтобы разрешить запись, нужно:
1. Убрать `read_only=True`
2. Переопределить метод `create()` или `update()`

```python
class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)  # read_only убран
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements')
    
    def create(self, validated_data):
        # Проверяем, есть ли достижения в запросе
        if 'achievements' not in self.initial_data:
            # Создаем котика без достижений
            return Cat.objects.create(**validated_data)
        
        # Извлекаем достижения из данных
        achievements = validated_data.pop('achievements')
        
        # Создаем котика
        cat = Cat.objects.create(**validated_data)
        
        # Обрабатываем каждое достижение
        for achievement in achievements:
            # get_or_create - получить существующее или создать новое
            current_achievement, _ = Achievement.objects.get_or_create(
                **achievement)
            # Создаем связь в промежуточной таблице
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat)
        
        return cat
```

### 6. Необязательные поля

Чтобы поле было необязательным, используйте `required=False`:

```python
class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
```

### 7. Доступ к исходным данным запроса

`self.initial_data` содержит原始 данные запроса (до валидации):

```python
def create(self, validated_data):
    # Проверяем, было ли поле в исходном запросе
    if 'achievements' not in self.initial_data:
        # Поле отсутствовало в запросе
        cat = Cat.objects.create(**validated_data)
        return cat
    # Поле было в запросе (возможно, пустое)
    achievements = validated_data.pop('achievements')
    # ... обработка достижений
```

### 8. Порядок работы при создании связанных объектов

1. Извлечь связанные данные из `validated_data`
2. Создать основной объект
3. Обработать каждый связанный объект:
   - Найти существующий или создать новый
   - Создать связи в промежуточных таблицах
4. Вернуть созданный объект

### 9. Важные параметры полей

| Параметр | Назначение |
|----------|------------|
| `many=True` | Для связей "один-ко-многим" и "многие-ко-многим" |
| `read_only=True` | Поле только для чтения (не участвует в записи) |
| `required=False` | Поле необязательное в запросе |

### 10. Шпаргалка по типам related-полей

| Тип поля | Описание 
|----------|----------|
| `PrimaryKeyRelatedField` | Возвращает/принимает id связанных объектов (по умолчанию) |
| `StringRelatedField` | Возвращает строковое представление (`__str__`) |
| `SlugRelatedField` | Возвращает/принимает значение указанного поля (slug) |
| `HyperlinkedRelatedField` | Возвращает ссылку на связанный объект |
| Вложенный сериализатор | Возвращает полный объект (JSON) |

### Разбор кода 

### 1. Сериализатор (`serializers.py`)

```python
from rest_framework import serializers
from .models import Post, Group

class PostSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        slug_field='slug',        # Какое поле группы использовать
        queryset=Group.objects.all(),  # Где искать группы
        required=False             # Поле необязательное
    )

    class Meta:
        fields = ('id', 'text', 'author', 'image', 'pub_date', 'group')
        model = Post
```

**Что здесь происходит:**

- **`SlugRelatedField`** — связывает посты с группами не по ID, а по полю `slug`
- **`slug_field='slug'`** — указывает, что для связи используется поле `slug` модели `Group`
- **`queryset=Group.objects.all()`** — все группы, среди которых можно выбирать
- **`required=False`** — группу можно не указывать при создании поста

**Как это работает в API:**
- **GET /posts/** → в поле `group` приходит `slug` группы (например `"python"`), а не её ID
- **POST /posts/** → в теле запроса можно передать `"group": "python"` (по slug)

### 2. ViewSet (`views.py`)

```python
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()      # Все посты
    serializer_class = PostSerializer   # Сериализатор для постов
```

**Что дает `ModelViewSet`:**
- **GET /posts/** → список всех постов
- **POST /posts/** → создать новый пост
- **GET /posts/{id}/** → получить конкретный пост
- **PUT /posts/{id}/** → полностью обновить пост
- **PATCH /posts/{id}/** → частично обновить пост
- **DELETE /posts/{id}/** → удалить пост

**Всё это работает "из коробки"** — не нужно писать отдельные методы!

### 3. Роутер и URL (`urls.py`)

```python
from django.urls import include, path
from rest_framework import routers
from .views import PostViewSet

router = routers.DefaultRouter()
router.register('api/v1/posts', PostViewSet)  # Регистрируем ViewSet

urlpatterns = [
    path('', include(router.urls)),  # Все маршруты из роутера
]
```

**Что делает роутер:**
- Автоматически создает все нужные URL для ViewSet
- `DefaultRouter` добавляет корневой эндпоинт `/` со списком всех ресурсов

**Сгенерированные URL:**
```
GET /api/v1/posts/              # список постов
POST /api/v1/posts/             # создать пост
GET /api/v1/posts/1/            # пост с id=1
PUT /api/v1/posts/1/            # обновить пост
PATCH /api/v1/posts/1/          # частично обновить
DELETE /api/v1/posts/1/         # удалить пост
```

## Ключевые моменты для памятки

### 🔥 **Сильные стороны этого кода:**

1. **Минимум кода** — вся логика CRUD в нескольких строках
2. **SlugRelatedField** — удобная работа со связанными моделями через человеко-читаемые поля
3. **required=False** — гибкость: группу можно не указывать
4. **ModelViewSet + DefaultRouter** — стандартный и мощный подход

### 📝 **Что можно добавить:**

```python
# В views.py — автоматическое проставление автора
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        # Автоматически подставляем текущего пользователя как автора
        serializer.save(author=self.request.user)
```

### 📊 **Структура ответа API:**

```json
GET /api/v1/posts/
[
    {
        "id": 1,
        "text": "Текст поста",
        "author": 1,
        "image": null,
        "pub_date": "2024-01-01T12:00:00Z",
        "group": "python"  // ← slug группы, а не ID!
    }
]
```

### 📤 **Пример запроса на создание:**

```json
POST /api/v1/posts/
{
    "text": "Мой первый пост",
    "group": "python",  // ← передаем slug группы
    "image": null
}
```

## Итог для памятки

Это **элегантное решение** для типового API:
- ✅ **DRF-стайл** — использует лучшие практики
- ✅ **Человеко-читаемые URL** — через slug, а не ID
- ✅ **Минимум кода** — максимум функциональности
- ✅ **Гибкость** — опциональные поля
- ✅ **Автоматические URL** — роутер всё создает сам


### Условие:
Добавьте к постам хештеги. Хештеги должны храниться в отдельной таблице в БД и быть связаны с постами отношением «многие-ко-многим».
При запросе постов должна возвращаться информация о всех связанных с конкретным постом хештегах, а при добавлении или обновлении поста нужно обеспечить возможность передавать названия хештегов списком прямо в теле запроса. Без указания хештегов пост через API тоже должен создаваться.
Пример POST-запроса для создания поста с хештегами:

{
    "text": "Текст для моего поста",
    "author": 1,
    "tag": [
        {"name": "хобби"},
        {"name": "личное"}
        ]
} 
### Код:
```python
from rest_framework import serializers

from .models import Group, Post, Tag, TagPost


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name',)
        model = Tag


class PostSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(slug_field='slug', queryset=Group.objects.all(), required=False)
    tag = TagSerializer(many=True, required=False)

    class Meta:
        fields = ('id', 'text', 'author', 'image', 'pub_date', 'group', 'tag', )
        model = Post

    def create(self, validated_data):
        if 'tag' not in self.initial_data:
            post = Post.objects.create(**validated_data)
            return post
        else:
            tags = validated_data.pop('tag')
            post = Post.objects.create(**validated_data)
            for tag in tags:
                current_tag, status = Tag.objects.get_or_create(**tag)
                TagPost.objects.create(tag=current_tag, post=post)
        return post
```

### Дополнительные настройки сериализаторов
### Супер-шпора Яндекса: https://code.s3.yandex.net/Python-dev/cheatsheets/044-drf-serializatory-i-validatory-dlja-svjazannyh-model/044-drf-serializatory-i-validatory-dlja-svjazannyh-model.html

### 1. SerializerMethodField — вычисляемые поля

Позволяет добавлять поля, которых нет в модели, вычисляя их "на лету".

```python
import datetime as dt
from rest_framework import serializers

class CatSerializer(serializers.ModelSerializer):
    # Определяем вычисляемое поле
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'age')
    
    # Метод для вычисления значения (get_<имя_поля>)
    def get_age(self, obj):
        # obj — текущий объект модели
        return dt.datetime.now().year - obj.birth_year
```

**Особенности:**
- Только для чтения (read-only)
- Метод вызывается для каждого объекта
- Не перегружать тяжелыми операциями
- Имя метода должно быть `get_<имя_поля>`

### 2. Пользовательские типы полей

Создание своего типа поля для кастомной обработки данных.

```python
import webcolors
from rest_framework import serializers

class Hex2NameColor(serializers.Field):
    # Чтение: из БД → JSON
    def to_representation(self, value):
        return value  # возвращаем как есть
    
    # Запись: из JSON → БД
    def to_internal_value(self, data):
        try:
            # Конвертируем hex-код в название цвета
            return webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')

# Использование в сериализаторе
class CatSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()  # свое поле
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color')
```

**Два обязательных метода:**
| Метод | Назначение | Когда вызывается |
|-------|------------|------------------|
| `to_representation(self, value)` | Преобразование для ответа | GET-запросы |
| `to_internal_value(self, data)` | Преобразование для записи | POST/PUT/PATCH |

### 3. Переименование полей: параметр `source`

Позволяет изменить имя поля в API, не меняя модель.

```python
class AchievementSerializer(serializers.ModelSerializer):
    # В API поле будет achievement_name, но связано с полем name модели
    achievement_name = serializers.CharField(source='name')
    
    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')
```

**Результат в JSON:**
```json
{
    "id": 1,
    "achievement_name": "поймал мышку"  // вместо "name"
}
```

**Работает как для чтения, так и для записи.**

### 4. Ограничение значений: ChoiceField

Ограничивает возможные значения поля заданным списком.

```python
# Определяем варианты выбора
COLOR_CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
)

class CatSerializer(serializers.ModelSerializer):
    # Поле принимает только значения из списка
    color = serializers.ChoiceField(choices=COLOR_CHOICES)
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year')
```

**Можно на уровне модели:**
```python
class Cat(models.Model):
    color = models.CharField(
        max_length=16, 
        choices=COLOR_CHOICES  # ограничение в БД
    )
```

### 5. Сравнение методов настройки полей

| Метод | Назначение | Пример |
|-------|------------|--------|
| **SerializerMethodField** | Вычисляемые поля | `age = serializers.SerializerMethodField()` |
| **Кастомное поле** | Своя логика преобразования | `color = Hex2NameColor()` |
| **source** | Переименование полей | `new_name = CharField(source='old_name')` |
| **ChoiceField** | Ограничение значений | `color = ChoiceField(choices=...)` |

### 6. Полный пример (Kittygram)

```python
import datetime as dt
import webcolors
from rest_framework import serializers
from .models import Cat, Achievement

COLOR_CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
)

# Кастомное поле
class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value
    
    def to_internal_value(self, data):
        try:
            return webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')

class AchievementSerializer(serializers.ModelSerializer):
    # Переименование поля
    achievement_name = serializers.CharField(source='name')
    
    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')

class CatSerializer(serializers.ModelSerializer):
    # Разные типы полей
    age = serializers.SerializerMethodField()        # вычисляемое
    color = Hex2NameColor()                          # кастомное
    achievements = AchievementSerializer(many=True)  # вложенное
    color_display = serializers.CharField(
        source='get_color_display', read_only=True
    )  # человекочитаемое значение choices
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'color_display', 
                  'birth_year', 'age', 'achievements')
    
    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year
```

### 7. Шпаргалка по ситуациям

| Ситуация | Решение |
|----------|---------|
| Нужно поле, которого нет в модели | `SerializerMethodField` |
| Нужно преобразовать данные при записи | Кастомное поле (`to_internal_value`) |
| Нужно преобразовать данные при чтении | Кастомное поле (`to_representation`) |
| Нужно переименовать поле в API | `source` параметр |
| Нужно ограничить допустимые значения | `ChoiceField` или `choices` в модели |
| Нужно получить display value для choices | `source='get_<field>_display'` |

### 8. Полезные ссылки

- [Документация DRF по полям](https://www.django-rest-framework.org/api-guide/fields/)
- [Кастомные поля](https://www.django-rest-framework.org/api-guide/fields/#custom-fields)
- [SerializerMethodField](https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield)


### Регулярные выражения (RegExp)
### Супер-шпора Яндекса: https://code.s3.yandex.net/Python-dev/cheatsheets/045-reguljarnye-vyrazhenija-shpora/045-reguljarnye-vyrazhenija-shpora.html

### 1. Что такое регулярные выражения

**Регулярные выражения** — это язык для поиска строк и проверки их на соответствие шаблону.

- **Pattern (шаблон/маска)** — строка-образец, определяющая правило поиска
- Позволяют находить строки по сложным критериям
- Широко используются в валидации данных (email, телефон, пароль)

### 2. Два типа символов в регулярных выражениях

| Тип | Описание | Пример |
|-----|----------|--------|
| **Спецсимволы** | Имеют специальное значение в шаблоне | `.` означает "любой символ" |
| **Обычные символы** | Должны точно совпадать в строке | `@` должен быть в email |

**Экранирование:** Чтобы использовать спецсимвол как обычный, ставят перед ним обратный слеш `\`
- `\.` — означает именно точку, а не "любой символ"

### 3. Пример: поиск email в доменах Yandex

```regex
^[\w.\-]{1,25}@(yandex\.ru|yandex\.ua|yandex\.by|yandex\.com)$
```

**Разбор шаблона:**

| Часть | Значение |
|-------|----------|
| `^` | Начало строки |
| `[\w.\-]` | Набор символов: буквы, цифры, _, точка, дефис |
| `{1,25}` | Длина от 1 до 25 символов |
| `@` | Символ @ (должен быть точно) |
| `(yandex\.ru\|yandex\.ua)` | Варианты доменов через `\|` (или) |
| `$` | Конец строки |

### 4. Основные спецсимволы

| Символ | Значение |
|--------|----------|
| `.` | Любой символ (кроме новой строки) |
| `^` | Начало строки |
| `$` | Конец строки |
| `*` | 0 или более повторений |
| `+` | 1 или более повторений |
| `?` | 0 или 1 повторение |
| `{n}` | Ровно n повторений |
| `{n,}` | n или более повторений |
| `{n,m}` | От n до m повторений |
| `\|` | Или (выбор между вариантами) |
| `(...)` | Группировка |
| `[...]` | Набор символов (любой из перечисленных) |
| `[^...]` | Любой символ, кроме перечисленных |

### 5. Метасимволы (группы символов)

| Метасимвол | Значение | Эквивалент |
|------------|----------|------------|
| `\d` | Любая цифра | `[0-9]` |
| `\D` | Любой не-цифровой символ | `[^0-9]` |
| `\w` | Буква, цифра или подчеркивание | `[a-zA-Z0-9_]` |
| `\W` | Любой кроме букв, цифр, _ | `[^a-zA-Z0-9_]` |
| `\s` | Пробельный символ | пробел, табуляция, перевод строки |
| `\S` | Непробельный символ | |

### 6. Примеры регулярных выражений

| Что ищем | Регулярное выражение | Пояснение |
|----------|---------------------|-----------|
| Email | `^[\w.+-]+@[\w-]+\.[a-z]{2,}$` | Локальная часть@домен.зона |
| Телефон | `^\+7\d{10}$` | +7 и 10 цифр |
| Только буквы | `^[a-zA-Zа-яА-Я]+$` | Только буквы (лат/кир) |
| IP-адрес | `^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$` | Четыре числа через точку |
| Дата (ГГГГ-ММ-ДД) | `^\d{4}-\d{2}-\d{2}$` | 2024-01-01 |

### 7. Использование в Django/DRF

**Валидация поля в сериализаторе:**
```python
from rest_framework import serializers
import re

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    phone = serializers.CharField()
    
    def validate_phone(self, value):
        # Проверка телефона через регулярное выражение
        pattern = r'^\+7\d{10}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                'Телефон должен быть в формате +7XXXXXXXXXX'
            )
        return value
```

**Валидация в моделях:**
```python
from django.db import models
from django.core.validators import RegexValidator

class User(models.Model):
    phone = models.CharField(
        max_length=12,
        validators=[
            RegexValidator(
                regex=r'^\+7\d{10}$',
                message='Телефон должен быть в формате +7XXXXXXXXXX'
            )
        ]
    )
```

### 8. Полезные ресурсы

- **Тестирование regex:** [regex101.com](https://regex101.com/) (выбрать Python flavor)
- **Документация Python:** [re — Regular expressions](https://docs.python.org/3/library/re.html)
- **Шпаргалка:** [Regex Cheat Sheet](https://www.debuggex.com/cheatsheet/regex/python)

### 9. Советы для новичков

1. **Начинай с простого:** сначала проверь простые совпадения, потом усложняй
2. **Используй онлайн-тестеры:** видишь сразу, что находит шаблон
3. **Экранируй спецсимволы:** если нужна точка, пиши `\.`
4. **Комментируй сложные regex:** в следующем месяце сам не вспомнишь, что означает твой шаблон
5. **Не усложняй:** часто простое решение лучше сложного regex

### 10. Пример с email из истории про Kittygram

```python
import re

# Шаблон для поиска email на доменах yandex
pattern = r'^[\w.\-]{1,25}@(yandex\.ru|yandex\.ua|yandex\.by|yandex\.com)$'

emails = [
    'ivan@yandex.ru',
    'petr@yandex.com',
    'test@gmail.com',
    'very_long_email_address_12345@yandex.ru'  # 26 символов - не подойдет
]

for email in emails:
    if re.match(pattern, email):
        print(f"Найден: {email}")

# Результат:
# Найден: ivan@yandex.ru
# Найден: petr@yandex.com
```


### Расширенные возможности вьюсетов

### 1. Стандартные действия (actions) во вьюсетах

| Действие | HTTP метод | URL | Назначение |
|----------|-----------|-----|------------|
| `create` | POST | `/cats/` | Создание объекта |
| `list` | GET | `/cats/` | Список объектов |
| `retrieve` | GET | `/cats/{id}/` | Получение одного объекта |
| `update` | PUT | `/cats/{id}/` | Полное обновление |
| `partial_update` | PATCH | `/cats/{id}/` | Частичное обновление |
| `destroy` | DELETE | `/cats/{id}/` | Удаление объекта |

### 2. Нестандартные действия: декоратор @action

Позволяет добавить кастомные методы во вьюсет.

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    
    # Кастомное действие: список из 5 белых котиков
    @action(detail=False, url_path='recent-white-cats')
    def recent_white_cats(self, request):
        cats = Cat.objects.filter(color='White')[:5]
        serializer = self.get_serializer(cats, many=True)
        return Response(serializer.data)
```

**Параметры декоратора @action:**

| Параметр | Описание | Пример |
|----------|----------|--------|
| `detail` | Работа с одним объектом (True) или коллекцией (False) | `detail=False` |
| `methods` | Разрешенные HTTP методы | `methods=['get', 'post']` |
| `url_path` | Кастомный URL (по умолчанию = имя метода) | `url_path='recent-white'` |

**Сгенерированный URL:** `/cats/recent-white-cats/`

### 3. Разные сериализаторы для одного вьюсета

Использование разных сериализаторов в зависимости от действия.

```python
class CatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color')  # только основные поля

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer  # по умолчанию
    
    def get_serializer_class(self):
        # Для списка используем облегченный сериализатор
        if self.action == 'list':
            return CatListSerializer
        # Для остальных действий - полный
        return CatSerializer
```

### 4. Миксины: сборка вьюсета под свои задачи

Миксины позволяют собрать вьюсет с любым набором действий.

**Предустановленные миксины:**

| Миксин | Действие | HTTP методы |
|--------|----------|-------------|
| `CreateModelMixin` | Создание | POST |
| `ListModelMixin` | Список | GET |
| `RetrieveModelMixin` | Один объект | GET |
| `UpdateModelMixin` | Обновление | PUT, PATCH |
| `DestroyModelMixin` | Удаление | DELETE |

**Пример: вьюсет только для создания и получения**
```python
from rest_framework import mixins, viewsets

class CreateRetrieveViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    pass  # ничего писать не нужно!

# Использование
class LightCatViewSet(CreateRetrieveViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
```

**Результат:**
- ✅ `POST /mycats/` — создать котика
- ✅ `GET /mycats/{id}/` — получить котика
- ❌ `GET /mycats/` — список (не работает)
- ❌ `PUT /mycats/{id}/` — обновление (не работает)

### 5. Регулярные выражения в роутерах

При регистрации вьюсета можно использовать regex для сложных URL.

```python
router.register(r'profile/(?P<username>[\w.@+-]+)/', UserViewSet)
# Будет обрабатывать:
# /profile/ivan/
# /profile/ivan.ivanov/
# /profile/user@example/
```

**r-строки** (raw strings) — строки с префиксом `r`, в которых escape-последовательности игнорируются.

### 6. Низкоуровневый ViewSet (наследование от ViewSet)

Для полного контроля можно наследоваться от `viewsets.ViewSet` и реализовать методы вручную.

```python
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class CatViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Cat.objects.all()
        serializer = CatSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Cat.objects.all()
        cat = get_object_or_404(queryset, pk=pk)
        serializer = CatSerializer(cat)
        return Response(serializer.data)
    
    # Можно реализовать и другие методы:
    # create(), update(), partial_update(), destroy()
```

**Доступные методы для переопределения:**
- `list(self, request)`
- `create(self, request)`
- `retrieve(self, request, pk=None)`
- `update(self, request, pk=None)`
- `partial_update(self, request, pk=None)`
- `destroy(self, request, pk=None)`

### 7. Иерархия классов в DRF

```
APIView
    └── GenericAPIView
        ├── GenericViewSet
        │   ├── ReadOnlyModelViewSet (list + retrieve)
        │   ├── ModelViewSet (все CRUD)
        │   └── Кастомные вьюсеты через миксины
        └── Mixins (Create, List, Retrieve, Update, Destroy)
```

### 8. Сравнение подходов

| Подход | Гибкость | Код | Когда использовать |
|--------|----------|-----|-------------------|
| **ModelViewSet** | Низкая | Минимум | Стандартный CRUD |
| **ReadOnlyModelViewSet** | Низкая | Минимум | Только чтение |
| **Миксины** | Средняя | Мало | Нужен определенный набор действий |
| **ViewSet** | Высокая | Много | Полный контроль, нестандартная логика |
| **@action** | Средняя | Средне | Добавить одно-два кастомных действия |

### 9. Полезные приемы

**Доступ к текущему действию:**
```python
def my_method(self, request):
    if self.action == 'list':
        # делаем одно
    elif self.action == 'retrieve':
        # делаем другое
```

**Кастомное действие с POST:**
```python
@action(detail=True, methods=['post'])
def set_color(self, request, pk=None):
    cat = self.get_object()
    cat.color = request.data.get('color')
    cat.save()
    return Response({'status': 'color updated'})
```

**URL:**
- `/cats/{id}/set_color/` — POST запрос для смены цвета

### 10. Шпаргалка

| Ситуация | Решение |
|----------|---------|
| Нужно кастомное действие | `@action(detail=False)` |
| Разные сериализаторы для разных запросов | `get_serializer_class()` |
| Нужен вьюсет только с create и retrieve | Миксины `CreateModelMixin` + `RetrieveModelMixin` |
| Нужен полный контроль над методами | Наследование от `ViewSet` |
| Сложные URL-шаблоны | Регулярные выражения в `router.register()` |

### JWT + Djoser аутентификация

### 1. Принципы аутентификации в REST API

**Stateless (отсутствие состояния)** — каждый запрос независим, сервер не хранит информацию о предыдущих запросах.

**Аутентификация по токенам:**
- Клиент получает токен один раз (по логину/паролю)
- При каждом запросе отправляет токен в заголовке
- Токен содержит всю информацию о пользователе

### 2. Встроенная аутентификация DRF: Authtoken

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework.authtoken',  # добавляем
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # доступ только авторизованным
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# urls.py
from rest_framework.authtoken import views

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),  # получение токена
]
```

**Использование:**
```bash
# Получить токен
POST /api-token-auth/
{
    "username": "user",
    "password": "pass"
}

# Ответ:
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}

# Запрос с токеном
GET /api/v1/posts/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 3. JWT (JSON Web Token) — преимущества

**Структура JWT:**
```
Header.Payload.Signature
```

**Header (заголовок):**
```json
{
  "alg": "HS256",      // алгоритм подписи
  "typ": "JWT"         // тип токена
}
```

**Payload (полезная нагрузка):**
```json
{
  "token_type": "access",
  "exp": 1578171903,   // срок действия
  "user_id": 5         // данные пользователя
}
```

**Signature (подпись):** гарантирует, что токен не был изменен

**Преимущества JWT:**
- Не нужно обращаться к БД при каждом запросе
- Вся информация уже в токене
- Можно проверить срок действия

### 4. Установка и настройка Djoser + Simple JWT

```bash
pip install djoser djangorestframework-simplejwt==4.7.2
```

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.auth',
    ...
    'rest_framework',
    'djoser',  # после rest_framework
]

from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # срок жизни токена
    'AUTH_HEADER_TYPES': ('Bearer',),  # тип заголовка
}

# urls.py
urlpatterns = [
    path('auth/', include('djoser.urls')),        # управление пользователями
    path('auth/', include('djoser.urls.jwt')),    # JWT эндпоинты
]
```

### 5. Эндпоинты Djoser

| Эндпоинт | Метод | Назначение |
|----------|-------|------------|
| `/auth/users/` | POST | Создать пользователя |
| `/auth/users/me/` | GET | Информация о текущем пользователе |
| `/auth/jwt/create/` | POST | Получить JWT токен |
| `/auth/jwt/refresh/` | POST | Обновить токен |
| `/auth/users/reset_password/` | POST | Сброс пароля |

### 6. Работа с JWT

**Создание пользователя:**
```bash
POST /auth/users/
{
    "username": "newuser",
    "password": "securepass123"
}
# Ответ: 201 Created
```

**Получение токена:**
```bash
POST /auth/jwt/create/
{
    "username": "newuser",
    "password": "securepass123"
}

# Ответ:
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Использование токена:**
```bash
GET /api/v1/posts/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Обновление токена:**
```bash
POST /auth/jwt/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Новый access-токен
{
    "access": "новый_токен..."
}
```

### 7. Кастомизация Djoser

**Переопределение сериализатора:**
```python
from djoser.serializers import UserSerializer

class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
```

**Переопределение вьюсета:**
```python
from djoser.views import UserViewSet
from .serializers import CustomUserSerializer

class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
```

### 8. Типы токенов

| Токен | Назначение | Срок жизни |
|-------|------------|------------|
| **access** | Основной токен для доступа к API | Короткий (день/час) |
| **refresh** | Для получения нового access токена | Длинный (неделя/месяц) |

### 9. Заголовки авторизации

**Authtoken:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**JWT:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 10. Обработка ошибок

| Ситуация | Статус | Ответ |
|----------|--------|-------|
| Нет токена | 401 | `{"detail": "Учетные данные не предоставлены"}` |
| Недействительный токен | 401 | `{"detail": "Invalid token"}` |
| Истек токен | 401 | `{"detail": "Token expired"}` |

### 11. Сравнение методов

| Характеристика | Authtoken | JWT |
|----------------|-----------|-----|
| Хранение данных | В БД | В токене |
| Запросы к БД | При каждом запросе | Только при получении токена |
| Масштабирование | Сложнее | Легче |
| Срок действия | Бесконечный (до отзыва) | Настраиваемый |
| Доп. библиотеки | Встроен в DRF | Simple JWT + Djoser |

### 12. Полезные ссылки

- [Документация Djoser](https://djoser.readthedocs.io/)
- [Документация Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT.io](https://jwt.io/) — декодирование и проверка токенов
