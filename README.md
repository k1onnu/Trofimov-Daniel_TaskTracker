# Task Tracker API

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.162-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-8.3-0A9EDC?style=flat&logo=pytest&logoColor=white)

Сервис для управления задачами. 
Проект представляет собой REST API на FastAPI с поддержкой аутентификации, фильтрации, аналитики и визуализации данных.

## Стек технологий
- **Язык:** Python 3.13
- **Фреймворк:** FastAPI
- **База данных:** PostgreSQL 16 (в Docker)
- **ORM:** SQLAlchemy 2.1 + Alembic (миграции)
- **Аутентификация:** JWT (PyJWT), хеширование паролей (Argon2)
- **Анализ данных:** Pandas
- **Визуализация:** Matplotlib
- **Тесты:** Pytest + httpx

## Запуск проекта

### 1. Клонирование и настройка
```bash
git clone https://github.com/k1onnu/Trofimov-Daniel_TaskTracker.git
cd Trofimov-Daniel_TaskTracker
python -m venv venv
# Активация venv:
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка окружения
Создайте файл `.env` в корне проекта (на основе `.env.example`):
```env
DATABASE_URL=postgresql://tracker:tracker@localhost:5433/tracker_db
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Запуск базы данных
```bash
docker compose up -d
```
*(PostgreSQL будет доступен на порту `5433`)*

### 4. Применение миграций
```bash
alembic upgrade head
```

### 5. Запуск сервера
```bash
uvicorn app.main:app --reload
```
Документация Swagger доступна по адресу: **http://127.0.0.1:8000/docs**

---

## Модель данных (ERD)

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string hashed_password
        datetime created_at
    }
    TASKS {
        int id PK
        string title
        text description
        enum status "new, in_progress, done, cancelled"
        enum priority "low, medium, high"
        datetime due_date
        datetime created_at
        datetime updated_at
        int assignee_id FK
    }
    USERS ||--o{ TASKS : "assignee"
```
*Связь: один пользователь (User) может быть исполнителем многих задач (Tasks).*

---

## Структура проекта

```text
Trofimov-Daniel_TaskTracker/
├── app/
│   ├── api/             # HTTP-эндпоинты (роутеры)
│   │   ├── analytics.py # Аналитика и графики
│   │   ├── tasks.py     # CRUD для задач
│   │   └── users.py     # Управление пользователями
│   ├── auth/            # JWT-аутентификация
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   └── router.py
│   ├── crud/            # Функции работы с БД
│   │   ├── task.py
│   │   └── user.py
│   ├── models/          # SQLAlchemy-модели (Таблицы)
│   │   ├── task.py
│   │   └── user.py
│   ├── schemas/         # Pydantic-схемы (Валидация данных)
│   │   ├── task.py
│   │   └── user.py
│   ├── config.py        # Настройки приложения (env)
│   ├── database.py      # Подключение к БД
│   ├── main.py          # Точка входа в приложение
│   └── security.py      # Хеширование паролей
├── migrations/          # Миграции Alembic
├── tests/               # Pytest-тесты
│   ├── conftest.py      # Фикстуры для тестов
│   ├── test_analytics.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_users.py
├── .env.example         # Пример переменных окружения
├── alembic.ini          # Конфигурация Alembic
├── docker-compose.yml   # Конфигурация PostgreSQL для Docker
├── requirements.txt     # Зависимости проекта
└── README.md            # Документация
```
---

## Основные эндпоинты

### Аутентификация
- `POST /auth/register` — регистрация нового пользователя
- `POST /auth/login` — получение JWT-токена (OAuth2 form-data)
- `GET /auth/me` — информация о текущем пользователе

### Пользователи
- `POST /users/` — создание пользователя (публичный)
- `GET /users/{id}` — получение пользователя по ID

### Задачи (CRUD)
- `POST /tasks/` — создание задачи *(требует токен)*
- `GET /tasks/` — список задач с фильтрацией (`?status=new&priority=high&assignee_id=1`)
- `GET /tasks/{id}` — получение задачи
- `PATCH /tasks/{id}` — обновление статуса/приоритета *(требует токен)*
- `DELETE /tasks/{id}` — удаление задачи *(требует токен)*

### Аналитика
- `GET /analytics/summary` — статистика по статусам, приоритетам и исполнителям (в формате JSON)
- `GET /analytics/chart` — визуализация распределения задач в виде PNG-графика (гистограммы)

---

## Безопасность
- Пароли хранятся в виде хешей (Argon2).
- Доступ к изменению данных защищен JWT-токенами.
- Защита от SQL-инъекций обеспечена использованием параметризованных запросов через SQLAlchemy ORM (без использования сырых SQL-строк).

---

## Тестирование
Проект покрыт тестами (Pytest) для всех ключевых эндпоинтов: CRUD задач, пользователей, аутентификация, фильтрация и аналитика.

Перед запуском тестов убедитесь, что контейнер с БД запущен (`docker compose up -d`).
```bash
pytest -v
```
*(Тесты используют отдельную базу данных `tracker_db_test`, которая создается и удаляется автоматически, не затрагивая рабочие данные).*