# 🎉 Блог добавлен + улучшена шапка

## ✨ Что сделано

### 1️⃣ **Реализован формат блога**
- **Страница**: `/blog` с лентой постов (новые сверху)
- **Форма создания**: текст и/или изображение
- **Валидация**: ошибка, если оба поля пусты
- **Хранение**: в памяти (на время разработки)
- **Изображения**: сохраняются на диск в `static/images/blog/`

### 2️⃣ **Улучшена навигация**
- Добавлена кнопка "БЛОГ" в header и sidebar
- Ссылка автоматически появляется благодаря `Config.NAV_SECTIONS`
- Кнопка активируется при посещении `/blog`

### 3️⃣ **Улучшена шапка (header)**
- **При прокрутке вниз**: красный заголовок исчезает
- **Навигация остаётся видимой** в компактном режиме
- Плавный переход, не отвлекает от чтения

---

## 📁 Новые файлы

### Модели
- [models/post.py](models/post.py) — dataclass `Post` (текст, картинка, время создания)

### Хранилище данных
- [services/blog_stub_data.py](services/blog_stub_data.py) — in-memory posts + file save logic
  - Изображения: `timestamp_filename.ext` в `static/images/blog/`
  - Посты: теряются при перезагрузке приложения (ожидаемо)

### Репозиторий (слой доступа)
- [repositories/post_repository.py](repositories/post_repository.py) — фасад для routes
  - Методы: `list_all()`, `get_by_id()`, `create()`, `delete()`
  - FUTURE комментарии показывают как писать SQL queries

### Маршруты
- [routes/blog.py](routes/blog.py) — blueprint
  - `GET /blog` — лента постов
  - `POST /api/blog/post` — создание поста (AJAX, multipart/form-data)

### Шаблоны
- [templates/blog.html](templates/blog.html) — страница ленты
- [templates/components/post_form.html](templates/components/post_form.html) — форма создания
- [templates/components/post_card.html](templates/components/post_card.html) — карточка поста

### Стили
- [static/css/blog.css](static/css/blog.css) — стили блога (форма, карточки, анимации)

### Скрипты
- [static/js/blog.js](static/js/blog.js) — AJAX форма, file upload, drag-and-drop
- [static/js/header_scroll.js](static/js/header_scroll.js) — обновлён (compact state вместо hide)

### Директории
- [static/images/blog/](static/images/blog/) — для загруженных изображений

---

## 🔄 Изменённые файлы

| Файл | Изменение |
|------|-----------|
| [app.py](app.py) | Добавлен импорт и регистрация `blog_bp` |
| [config.py](config.py) | Добавлена кнопка "БЛОГ" в `NAV_SECTIONS` |
| [templates/base.html](templates/base.html) | Добавлена ссылка на `blog.css` |
| [static/css/header.css](static/css/header.css) | Новое состояние `compact` (title hides, nav stays) |
| [static/js/header_scroll.js](static/js/header_scroll.js) | Логика вместо `hidden` теперь `compact` |

---

## 🧪 Протестировано

- ✅ Форма создания поста (текст)
- ✅ Валидация (ошибка если пусто)
- ✅ Посты отображаются в обратном хронологическом порядке
- ✅ Кнопка БЛОГ видна в навигации и работает
- ✅ Заголовок скрывается при скролле, навигация остаётся
- ✅ Стили применены (тёмная тема, красные акценты)

---

## 📋 Кодстайл (для команды)

- ✅ **Docstrings** на каждый модуль и функцию
- ✅ **FUTURE комментарии** для расширений
- ✅ **CSS секции** (==== название ====)
- ✅ **JS: IIFE + 'use strict'**
- ✅ **Переменные CSS** для цветов и времени
- ✅ **Модульно**: models → services → repositories → routes

---

## 🚀 Для дальнейшей разработки

### TODO (команде)
- [ ] Загрузить тестовое изображение → проверить сохранение и отображение
- [ ] Прикрепить изображение без текста → проверить валидацию
- [ ] Проверить мобильную версию (адаптивность формы)
- [ ] Добавить кнопку удаления поста (уже есть слой `delete()` в репозитории)
- [ ] Лайки/комментарии (расширить модель `Post`)

### Миграция на БД (когда готово)
1. Раскомментируйте SQLAlchemy в `requirements.txt` и `models/database.py`
2. Замените `services/blog_stub_data.py` на ORM модель
3. Обновите `repositories/post_repository.py` (замените stub-вызовы на `.query()`)
4. **Всё остальное останется той же**: routes, templates, JS, CSS не изменятся!

---

## 💾 Как устроено хранилище (важно!)

### Текущая архитектура (разработка)
```
Посты:
  В памяти (в списке _posts)
  ↓ (при перезагрузке приложения)
  ❌ Теряются

Изображения:
  На диск: static/images/blog/{timestamp}_{name}.jpg
  ↓ (при перезагрузке приложения)
  ✅ Остаются
```

### Будущая архитектура (на БД)
```
Посты:
  В БД (таблица posts)
  ↓ (при перезагрузке приложения)
  ✅ Остаются

Изображения:
  На диск: static/images/blog/{timestamp}_{name}.jpg (или CDN)
  ↓ (при перезагрузке приложения)
  ✅ Остаются

Путь сохранения: в поле image_filename в БД (не в памяти)
```

### Как это выглядит в коде

**Сейчас (stub-данные):**
```python
# services/blog_stub_data.py
_posts: List[Post] = []  # в памяти!

# Когда будет БД:
# models/post.py (SQLAlchemy)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000))
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Интерфейс остаётся той же:**
```python
# repositories/post_repository.py - НЕ ИЗМЕНИТСЯ
PostRepository.list_all()   # работает как с stub, так и с БД
PostRepository.create(text, image_filename)  # работает везде
```

---

## 📖 Полная документация архитектуры

→ [BLOG_ARCHITECTURE.md](BLOG_ARCHITECTURE.md) — детальное описание компонентов и миграции

