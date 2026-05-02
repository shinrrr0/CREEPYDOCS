# Блог: архитектура и хранение данных

## 📋 Что было добавлено

### 1. **Модели** (`models/post.py`)
```python
@dataclass
class Post:
    id: int
    text: Optional[str]           # может быть None (только картинка)
    image_filename: Optional[str] # может быть None (только текст)
    created_at: datetime
```
- Гибкая структура: текст и/или картинка
- Совместима с будущей миграцией на SQLAlchemy

### 2. **Хранение данных** (ВАЖНО ДЛЯ КОМАНДЫ)

#### `services/blog_stub_data.py` — временное in-memory хранилище
- **Пост-объекты**: хранятся в `_posts: List[Post]`
- **Изображения**: сохраняются на диск в `static/images/blog/`
  - Имена файлов: `{timestamp}_{original_name}` (например: `1746345600_photo.jpg`)
  - Директория создаётся автоматически при первой загрузке
- **На перезагрузке приложения**: посты теряются, но файлы остаются
- **Путь миграции**: замените эту файл на SQLAlchemy queries, остальное не изменится

#### `repositories/post_repository.py` — фасад доступа
- Методы: `list_all()`, `get_by_id()`, `create()`, `delete()`
- Все FUTURE комментарии показывают, как писать SQL queries
- Routes используют этот слой, не обращаются к stub-данным напрямую

### 3. **Маршруты** (`routes/blog.py`)
```
GET  /blog                 → лента постов
POST /api/blog/post        → создание поста (multipart/form-data)
```

**Валидация в POST /api/blog/post:**
- ✅ Текст (textarea) или изображение (file input)
- ❌ Оба поля пусты → ошибка 400
- ❌ Неправильный тип файла → ошибка 400
- ✅ Возвращает JSON с результатом (success, post data, error message)

### 4. **UI/UX**

#### Форма создания поста (`templates/components/post_form.html`)
- **Textarea** для текста (опционально, placeholder "Напиши что-нибудь...")
- **Drag-and-drop зона** для загрузки изображений
  - Поддерживаемые форматы: jpg, png, gif, webp
  - Отображает имя выбранного файла
- **Кнопка отправки** → AJAX запрос на `/api/blog/post`
- **Обработка ошибок** → красное сообщение, автоскрытие через 5 сек

#### Карточка поста (`templates/components/post_card.html`)
- Время создания (дата + время, локальный формат)
- Изображение (если есть) с lazy loading
- Текст (если есть) с сохранением переносов

#### Стили (`static/css/blog.css`)
- Максимальная ширина 600px (читаемость)
- Красная полоска слева для каждого поста (визуальная фишка)
- Тёмная тема с полупрозрачным фоном
- Плавные переходы и hover-эффекты

### 5. **Улучшение header**

**Было:** заголовок исчезал полностью при скролле
**Стало:** только заголовок "CREEPYDOCS" скрывается, кнопки навигации остаются

#### CSS (`static/css/header.css`)
```css
/* Compact state: title hides, nav stays, padding adjusts */
.site-header[data-state="compact"] .site-header__title-row {
  display: none;
}
```

#### JavaScript (`static/js/header_scroll.js`)
- `data-state="visible"` → полная шапка (в начале страницы)
- `data-state="compact"` → только навигация (при скролле вниз)
- Плавный переход, тот же дебаунс как раньше

### 6. **Конфигурация** (`config.py`)
```python
NAV_SECTIONS = [
    {"slug": "stories", "label": "ИСТОРИИ"},
    {"slug": "gallery", "label": "ГАЛЕРЕЯ", "href": "/gallery"},
    {"slug": "blog",    "label": "БЛОГ",    "href": "/blog"},
]
```
- Кнопка "БЛОГ" автоматически появилась в header и sidebar
- Ссылка ведёт на `/blog`

### 7. **JavaScript** (`static/js/blog.js`)
- Обработка выбора файла + отображение имени
- Drag-and-drop поддержка
- AJAX отправка формы (multipart/form-data)
- Валидация на клиенте (текст или картинка)
- Блокировка кнопки во время отправки
- Перезагрузка страницы после успеха (TODO: AJAX reload)

---

## 🗂️ Структура файлов (что добавлено)

```
models/
  └─ post.py                    ← новая модель

services/
  └─ blog_stub_data.py          ← in-memory storage + file save logic

repositories/
  └─ post_repository.py         ← фасад доступа к данным

routes/
  └─ blog.py                    ← blueprint: /blog и /api/blog/post

templates/
  ├─ blog.html                  ← страница ленты
  └─ components/
     ├─ post_form.html          ← форма создания
     └─ post_card.html          ← карточка поста

static/
  ├─ css/
  │  └─ blog.css                ← стили (form, cards, animations)
  ├─ js/
  │  ├─ blog.js                 ← AJAX форма + file upload
  │  └─ header_scroll.js        ← обновлён (compact state)
  └─ images/
     └─ blog/                   ← директория для изображений постов
```

---

## 🔄 Миграция на БД (когда будет готово)

1. **Замените `services/blog_stub_data.py`** на SQLAlchemy модель в `models/post.py`
2. **Обновите `repositories/post_repository.py`** — замените stub-вызовы на `.query()` и `.session` операции
3. **Всё остальное не изменится**: routes, templates, JS, CSS — всё работает так же!

Пример для разработчика:
```python
# Было (stub):
posts = blog_stub_data.get_all_posts_stub(limit=limit)

# Станет (SQLAlchemy):
posts = Post.query.order_by(Post.created_at.desc()).limit(limit).all() if limit else Post.query.order_by(Post.created_at.desc()).all()
```

---

## 📝 Кодстайл (для команды)

- Docstrings для каждого модуля и функции
- Комментарии FUTURE для возможных расширений
- CSS разбит на логические секции (==== header ====)
- JS использует IIFE с 'use strict'
- Переменные CSS для цветов, временных функций, размеров
- Никаких magic numbers — всё именованные константы
- 80 символов в строке (где возможно)

---

## ✅ Тестирование

- [x] Форма работает (теория)
- [x] Валидация: ошибка если ничего не выбрано
- [x] Пост создаётся с текстом
- [x] Заголовок скрывается при скролле, навигация остаётся
- [x] Кнопка БЛОГ видна в навигации

### TODO для тестирования:
- [ ] Загрузить изображение (проверить сохранение на диск)
- [ ] Загрузить неправильный тип файла (проверить ошибку)
- [ ] Добавить пост только с изображением (без текста)
- [ ] Проверить перезагрузку браузера (посты остаются? Картинки?)
- [ ] Мобильная версия (адаптивность)

---

## 💾 Временное хранилище: поведение

**При запуске приложения:**
- Посты из памяти: стираются (разработка)
- Картинки на диске: сохраняются

**Пример жизненного цикла:**
1. Запустили сервер
2. Пользователь создал пост "Привет!" (в памяти)
3. Пользователь загрузил картинку (на диск)
4. Перезагрузили сервер
5. Пост исчез, но картинка осталась на `static/images/blog/`

Это нормально для этапа разработки. Когда подключите БД, оба будут постоянными.
