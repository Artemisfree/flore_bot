import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("URL_JS")
CHAT_IDS = [
    int(chat_id.strip()) for chat_id in os.getenv("CHAT_IDS").split(",")
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

ORDER_STATUSES = {
    "PAID": "New paid order",
    "IN_PREPARATION": "In preparation",
    "IN_DELIVERY": "In delivery",
    "DELIVERED": "Delivered",
    "CANCELLED": "Cancelled"
}


def generate_status_buttons(order_id):
    buttons = []
    row = []
    for i, (code, label) in enumerate(ORDER_STATUSES.items(), start=1):
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=f"set_status:{order_id}:{code}"
        ))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
