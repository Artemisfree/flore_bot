from fastapi import FastAPI, Query
from pydantic import BaseModel
from flore_bot.bot import bot, generate_status_buttons, CHAT_IDS
from flore_bot.logger import logger

app = FastAPI()


class Order(BaseModel):
    orderId: str
    customerName: str
    totalAmount: float
    email: str
    phone: str
    address: str
    notes: str
    items: list[dict]
    status: str


@app.post("/notify_new_order")
async def notify(order: Order):
    text = (
        f"🛒 New Order #{order.orderId}\n"
        f"👤 Customer: {order.customerName}\n"
        f"📧 Email: {order.email}\n"
        f"📱 Phone: {order.phone}\n"
        f"📍 Address: {order.address}\n"
        f"📝 Notes: {order.notes}\n"
        f"💰 Total: {order.totalAmount}$\n"
        f"📦 Status: {order.status}"
    )

    for chat_id in CHAT_IDS:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=generate_status_buttons(order.orderId)
            )
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {chat_id}: {e}")
    return {"message": "Notification sent"}


@app.post("/notify_status_update")
async def notify_status_update(order: Order, previousStatus: str = Query(...)):
    if not previousStatus:
        previousStatus = order.previousStatus or "—"

    text = (
        f"🛒 Order #{order.orderId}\n"
        f"👤 Customer: {order.customerName}\n"
        f"📧 Email: {order.email}\n"
        f"📱 Phone: {order.phone}\n"
        f"📍 Address: {order.address}\n"
        f"📝 Notes: {order.notes}\n"
        f"💰 Total: {order.totalAmount}$\n"
        f"📦 Status: {previousStatus} ➡️ {order.status}"
    )

    for chat_id in CHAT_IDS:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=generate_status_buttons(order.orderId)
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке статуса пользователю {chat_id}: {e}")
    return {"message": "Status update sent"}
