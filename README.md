# Resume Analyzer

Resume Analyzer - сервис для анализа вакансий и резюме. Проект получает вакансии и резюме, обрабатывает их через LLM, считает степень соответствия кандидата вакансии и отправляет уведомления в Telegram.

## Что входит в проект

- `bot_service` - Telegram-бот для взаимодействия с пользователем.
- `vacancy_processing_service` - обработка и структурирование вакансий.
- `resume_parser_service` - получение резюме из HeadHunter.
- `resume_processing_service` - обработка и структурирование резюме.
- `matching_service` - расчет соответствия резюме вакансиям.
- `notification_service` - отправка уведомлений о найденных совпадениях.
- `migration_service` - миграции базы данных.

## Требования

- Docker и Docker Compose.
- `make`.
- `uv`, если нужно запускать миграции или сервисы локально без Docker.

## Настройка `.env`

Создайте `.env` в корне проекта на основе примера:

```bash
cp .env.example .env
```

Минимально нужно проверить и заполнить:

```env
# Postgres
POSTGRES_DB=resume_analyzer
POSTGRES_USER=root_user
POSTGRES_PASSWORD=root_password

# Redis
REDIS_PASSWORD=root_password

# LLM
LLM_NAME=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your_llm_api_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# HeadHunter
HEADHUNTER_TOKEN=your_hh_token
```

Остальные переменные в `.env.example` уже имеют рабочие значения по умолчанию для локального запуска. При необходимости можно поменять порты Postgres и Redis, параметры HeadHunter и лимиты consumer-сервисов.

## Запуск

Запустить только инфраструктуру: Postgres и Redis.

```bash
make start-d
```

Запустить всю платформу: инфраструктуру, миграции и все сервисы.

```bash
make platform-start-d
```

Посмотреть логи:

```bash
docker compose -f infra/docker/docker-compose.local.yml --env-file .env logs -f
```

Остановить инфраструктуру:

```bash
make down
```

Остановить все сервисы платформы:

```bash
make platform-down
```

## Миграции

Применить миграции локально:

```bash
make migrate-up
```

Откатить последнюю миграцию:

```bash
make migrate-down
```

Создать новую миграцию:

```bash
make migrate-revision m="migration name"
```
