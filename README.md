# Flore Order Bot

Telegram-бот для управления заказами цветочного магазина: поиск заказов, просмотр деталей, смена статуса и отправка уведомлений.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Aiogram](https://img.shields.io/badge/aiogram-3.x-green)
![FastAPI](https://img.shields.io/badge/FastAPI-async--api-teal)
![Poetry](https://img.shields.io/badge/poetry-dependency--manager-purple)

---

## Возможности

- Поиск заказа по ID (через команду или кнопку)
- Отображение информации о заказе (включая изображение и размер букета)
- Смена статуса заказа через инлайн-кнопки (по 3 в ряд)
- Удаление предыдущего сообщения с кнопками при смене статуса
- Уведомления о новых заказах и изменениях статусов (через FastAPI webhook-и)
- Поддержка отправки в несколько Telegram-чатов

---

## Стек технологий

- Python 3.11+
- Aiogram 3
- FastAPI
- httpx
- python-dotenv
- Poetry

---

## Установка

1. Клонировать проект:

```bash
git clone https://github.com/yourname/flore-order-bot.git
cd flore-order-bot
```

2. Установить зависимости:

```bash
poetry install
```

3. Создать файл .env с переменными окружения:

```bash
BOT_TOKEN=your_bot_token
URL_JS=https://your-backend-url.com
CHAT_IDS=123456789,987654321
```

# Запуск
### Режим бота (Polling):

```bash
poetry run python -m flore_bot
```


### Режим API (Webhook):

```bash
poetry run uvicorn flore_bot.api:app --reload
```

# Команды
### Команда	Описание

```bash
/start	Запуск и отображение кнопок
/help	Справка по использованию бота
/find <id>	Поиск заказа по ID
Инлайн-кнопки	Смена статуса заказа
```
Кнопки	Позволяют сменить статус заказа

# Webhook-и (FastAPI)

```bash
POST /notify_new_order
```
Отправляет уведомление о новом заказе.

Пример запроса:

```bash
{
  "orderId": "abc123",
  "customerName": "Имя",
  "totalAmount": 295.0,
  "email": "email@example.com",
  "phone": "0501234567",
  "address": "Dubai",
  "notes": "оставить у двери",
  "items": [
    {
      "title": "Peony Bouquet",
      "size": "M",
      "imageUrl": "https://example.com/image.jpg"
    }
  ],
  "status": "New paid order"
}
```

```bash
POST /notify_status_update?previousStatus=In%20delivery
```
Отправляет уведомление об изменении статуса.


# Структура проекта

```bash
flore_bot/
├── bot.py              # Настройка бота и глобальных переменных
├── handlers.py         # Команды и кнопки
├── callbacks.py        # Обработка инлайн-кнопок
├── api.py              # FastAPI endpoints
├── logger.py           # Логирование
├── __init__.py
├── ...
```

# Особенности реализации

* Кнопки статусов генерируются динамически (generate_status_buttons)
* После смены статуса предыдущее сообщение с кнопками удаляется (callback.message.delete())
* Все уведомления рассылаются в чаты, указанные в .env > CHAT_IDS
