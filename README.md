### Payment Service – тестовый сервис выплат

**Стек**: Django 5 + DRF, Celery, Redis, PostgreSQL, uv, drf-spectacular (Swagger/Redoc).

#### Структура и основная логика

- **Модель `Payout`**: сумма, валюта, реквизиты получателя, статус (`pending/processing/completed/failed`), описание, даты создания/обновления.
- **REST API (DRF)**: CRUD эндпоинты для заявок, отдельный action `retry` для повторной обработки.
- **Celery + Redis**: при создании заявки запускается задача `process_payout`, которая:
  - принимает `payout_id`,
  - помечает заявку в статус `processing`,
  - имитирует внешнюю обработку (задержка),
  - переводит заявку в статус `completed` или логирует ошибку.

#### Установка и запуск локально (без Docker)

- **1. Установка зависимостей**

```bash
cd /home/zhukata/projects/payment_service
uv sync
```

- **2. Пример env (локально)**

Скопируйте файл `env.example` в `.env` и при необходимости поправьте значения для локальной разработки (первая секция файла).

- **3. Миграции**

```bash
make migrate
```

- **4. Запуск приложения (dev)**

```bash
make run
```

- **5. Запуск Celery worker**

```bash
make worker
```

- **6. Запуск тестов**

```bash
make test
```

#### REST API

- **Список заявок**: `GET /api/payouts/`
- **Создание заявки**: `POST /api/payouts/`
- **Получение заявки**: `GET /api/payouts/{id}/`
- **Частичное обновление (в т.ч. статуса)**: `PATCH /api/payouts/{id}/`
- **Удаление заявки**: `DELETE /api/payouts/{id}/`
- **Повторная обработка**: `POST /api/payouts/{id}/retry/`

#### Документация Swagger / Redoc

- **OpenAPI схема (json/yaml)**: `GET /api/schema/`
- **Swagger UI**: `GET /api/docs/`
- **Redoc**: `GET /api/redoc/`

Схема генерируется автоматически на основе DRF-вьюх и сериализаторов (drf-spectacular).

#### Запуск через Docker / docker-compose

- **1. Собрать и поднять сервисы**

```bash
docker-compose up --build
```

По умолчанию поднимаются:

- **web**: Django-приложение (`http://localhost:8000`);
- **worker**: Celery worker;
- **db**: PostgreSQL 16;
- **redis**: Redis 7.

- **2. Миграции внутри контейнера**

```bash
docker-compose exec web uv run python manage.py makemigrations
docker-compose exec web uv run python manage.py migrate
```

- **3. Пример `.env` для docker-compose**

Используйте вторую секцию файла `env.example` (для Docker) и сохраните её в `.env` в корне проекта.

#### Тесты

Минимальные тесты находятся в `payouts/tests.py`:

- **успешное создание заявки** и проверка полей;
- **проверка, что при создании заявки вызывается Celery-задача** (через `mock`).

Запуск: `make test` или `uv run python manage.py test`.

#### CI (GitHub Actions)


#### Описание деплоя (production)

- **Сервисы**:
  - web (Django под gunicorn/uvicorn за nginx/ingress);
  - PostgreSQL (managed/кластер);
  - Redis/RabbitMQ для Celery;
  - Celery worker (+ Celery beat при необходимости);
  - система логирования и мониторинга (например, Prometheus + Grafana, Sentry).

- **Базовые шаги подготовки**:
  - поднять БД и брокер;
  - настроить секреты (через переменные окружения/secret manager);
  - прогнать миграции;
  - запустить web-приложение и worker-ы;
  - настроить health-check-и, алерты и резервное копирование БД.

