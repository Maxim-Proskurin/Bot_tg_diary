# Diary Bot 📝

[![CI](https://img.shields.io/github/actions/workflow/status/Maxim-Proskurin/Bot_tg_diary/ci.yml?branch=main&label=CI)](https://github.com/Maxim-Proskurin/Bot_tg_diary/actions)
[![codecov](https://img.shields.io/codecov/c/github/Maxim-Proskurin/Bot_tg_diary?label=coverage)](https://codecov.io/gh/Maxim-Proskurin/Bot_tg_diary)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Автор: **Максим Проскурин**

---

## Стек технологий

- **Python 3.12+** — асинхронный стиль программирования.
- **aiogram 3.x** — современный асинхронный Telegram Bot Framework (FSM, команды, кнопки, состояния).
- **SQLAlchemy 2.x (async)** — асинхронный ORM для работы с PostgreSQL.
- **PostgreSQL** — реляционная база данных для хранения пользователей и заметок.
- **alembic** — миграции для управления схемой базы данных (создание/изменение таблиц, версионирование структуры).
- **python‑dotenv** — загрузка переменных окружения из `.env` (секреты, строки подключения).
- **poetry** — менеджер зависимостей и виртуального окружения.
- **pytest, pytest‑asyncio** — тестирование асинхронного кода.
- **flake8, black** — линтинг и автоформатирование кода.

---

## CI / CD

| Этап               | Что происходит                                           |
| ------------------ | -------------------------------------------------------- |
| **Lint & Format**  | Проверка кода `flake8` и форматирование `black --check`. |
| **Tests**          | Запуск unit‑тестов `pytest` с покрытием `pytest‑cov`.    |
| **Build & Deploy** | (опционально) публикация контейнера/релиза.              |

CI запускается через **GitHub Actions** (см. `.github/workflows/ci.yml`).

---

## Структура проекта

├── bot.py               # точка входа, регистрация хендлеров, запуск бота
├── handlers/            # хендлеры для команд (add, list, edit, delete, find, ...)
│   └── __init__.py      # каждый хендлер построен с поддержкой FSM
├── db/
│   ├── models.py        # SQLAlchemy‑модели (User, Note, ...)
│   └── session.py       # создание асинхронной сессии
├── alembic/             # миграции alembic (env.py, versions/*)
├── tests/               # unit‑тесты бизнес‑логики и хендлеров
├── .env.example         # пример файла переменных окружения
└── pyproject.toml       # зависимости poetry

---

## Быстрый старт

```bash
# 1. Клонируем репозиторий
git clone https://github.com/Maxim-Proskurin/Bot_tg_diary.git
cd Bot_tg_diary

# 2. Устанавливаем зависимости через Poetry
pip install poetry
poetry install

# 3. Копируем переменные окружения
cp .env.example [.env](VALID_FILE)
# ... заполняем токен бота и строку подключения к БД ...

# 4. Запускаем миграции и бота
poetry run alembic upgrade head
poetry run python [bot.py](VALID_FILE)

# Запуск тестов
poetry run pytest

# Проверка покрытия кода
poetry run pytest --cov=handlers --cov=db --cov-report=term-missing

# Проверка кода линтером
poetry run flake8

# Автоформатирование
poetry run black .


# пример .env

BOT_TOKEN=Твой_токен_бота
DB_HOST=localhost
DB_PORT=5432
DB_USER_NAME=postgres
DB_PASSWORD=пароль_от_бд
DB_NAME=имя_бд
DATABASE_URL=postgresql+asyncpg://postgres:пароль_от_бд@localhost:5432/имя_бд
