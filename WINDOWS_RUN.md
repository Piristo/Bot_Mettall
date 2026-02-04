# Запуск бота в Windows

## Шаг 1: Откройте командную строку

Нажмите `Win + R`, введите `cmd`, нажмите Enter

## Шаг 2: Перейдите в папку с ботом

```cmd
cd C:\Users\Nikolay\Desktop\AGSkill\Timon\metallica-archive-bot
```

## Шаг 3: Запустите Docker

```cmd
docker-compose up -d
```

## Шаг 4: Проверьте статус

```cmd
docker ps
```

Должно быть два контейнера: metallica-bot и metallica-redis

## Шаг 5: Посмотреть логи

```cmd
docker logs metallica-bot
```

## Остановка бота

```cmd
docker-compose down
```
