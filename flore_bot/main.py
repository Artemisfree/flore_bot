from typing import Optional
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
    deliveryTime: Optional[str] = None


@app.post("/notify_new_order")
async def notify(order: Order):
    # Основной текст заказа
    text = (
        f"🛒 New Order #{order.orderId}\n"
        f"👤 Customer: {order.customerName}\n"
        f"📧 Email: {order.email}\n"
        f"📱 Phone: {order.phone}\n"
        f"📍 Address: {order.address}\n"
        f"🕒 Delivery time: {order.deliveryTime or 'Not specified'}\n"
        f"📝 Notes: {order.notes}\n"
        f"💰 Total: {order.totalAmount} AED\n"
        f"📦 Status: {order.status}\n"
    )

    for item in order.items:
        text += f"🪻 Title: {item.get('title', 'Item')}\n"
        text += f"📏 Size: {item.get('size', '')}\n"

    first_image_url = None
    for item in order.items:
        url = item.get("imageUrl")
        if url and url.startswith("http"):
            first_image_url = url
            break

    for chat_id in CHAT_IDS:
        try:
            if first_image_url:
                logger.info(f"Отправка фото с описанием: {first_image_url}")
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=first_image_url,
                    caption=text,
                    reply_markup=generate_status_buttons(order.orderId)
                )
            else:
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
        f"🕒 Delivery time: {order.deliveryTime or 'Not specified'}\n"
        f"📝 Notes: {order.notes}\n"
        f"💰 Total: {order.totalAmount} AED\n"
        f"📦 Status: {previousStatus} ➡️ {order.status}\n"
    )

    logger.info(f"[notify_status_update] Items: {order.items}")
    for item in order.items:
        text += f"🪻 Title: {item.get('title', 'Item')}\n"
        text += f"📏 Size: {item.get('size', '')}\n"
    
    logger.info(f"[notify_status_update] chat_ids: {CHAT_IDS}")
    logger.info(f"[notify_status_update] caption length: {len(text)}")
    logger.info(f"[notify_status_update] deliveryTime: {order.deliveryTime}")

    first_image_url = None
    for item in order.items:
        url = item.get("imageUrl")
        if url and url.startswith("http"):
            first_image_url = url
            break

    logger.info(f"[notify_status_update] Отправка в чаты: {CHAT_IDS}")
    for chat_id in CHAT_IDS:
        try:
            logger.info(f"[notify_status_update] Sending to chat_id: {chat_id}")
            logger.info(f"[notify_status_update] first_image_url: {first_image_url}")
            if first_image_url:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=first_image_url,
                    caption=text,
                    reply_markup=generate_status_buttons(order.orderId)
                )
                logger.info(f"[notify_status_update] Photo sent to {chat_id}")
            else:
                logger.info(f"[notify_status_update] Trying to send message to {chat_id}")
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=generate_status_buttons(order.orderId)
                )
                logger.info(f"[notify_status_update] Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке статуса пользователю {chat_id}: {e}")
    return {"message": "Status update sent"}
