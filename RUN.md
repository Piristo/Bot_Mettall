# Быстрый запуск Metallica Archive Bot

## 1. Настройка токенов

Откройте файл `.env` и добавьте ваши токены:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**Как получить токены:**

- **Telegram:** @BotFather -> /newbot
- **YouTube:** Google Cloud Console -> YouTube Data API v3

## 2. Запуск Docker

```bash
cd metallica-archive-bot
docker-compose up -d
```

## 3. Проверка

```bash
docker ps                    # статус контейнеров
docker logs -f metallica-bot # логи бота
```

## Команды Docker

| Команда | Описание |
|---------|----------|
| `docker-compose up -d` | Запуск в фоне |
| `docker-compose down` | Остановка |
| `docker logs -f metallica-bot` | Логи в реальном времени |
| `docker restart metallica-bot` | Перезапуск бота |

## Остановка

```bash
docker-compose down
```
