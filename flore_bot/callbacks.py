from aiogram import types, Router
from flore_bot.bot import bot, ORDER_STATUSES, URL
import httpx
from flore_bot.logger import logger

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("set_status:"))
async def handle_status_change(callback: types.CallbackQuery):
    _, order_id, new_status_code = callback.data.split(":")
    js_status = ORDER_STATUSES[new_status_code]

    await bot.answer_callback_query(callback.id, text="Обрабатываю...")

    try:
        async with httpx.AsyncClient() as client:
            old_order_response = await client.get(
                f"{URL}/api/orders/{order_id}",
                headers={"is-admin": "true"}
            )
            old_order = old_order_response.json()
            old_status = old_order["status"]
            response = await client.patch(
                f"{URL}/api/orders/{order_id}/status",
                json={"status": js_status},
                headers={"is-admin": "true"}
            )
            logger.info(f"PATCH status code: {response.status_code}")
            logger.info(
                f"Response text: {response.text}, {callback.message.chat.id}, {callback.message.chat.username}"
            )

            if response.status_code == 200:
                # После обновления — сразу получаем заказ из API
                get_response = await client.get(
                    f"{URL}/api/orders/{order_id}",
                    headers={"is-admin": "true"}
                )
                order = get_response.json()

                # Собираем новый текст для сообщения
                payload = {
                    "orderId":    order["_id"],
                    "customerName": order["customerName"],
                    "totalAmount":  order["totalAmount"],
                    "email":         order["email"],
                    "phone":         order["phone"],
                    "address":       order["address"],
                    "notes":         order["notes"],
                    "items":         order["items"],
                    "status":       order["status"],
                    "previousStatus": old_status
                }
                params = {"previousStatus": old_status}
                await client.post(
                    f"{URL}/notify_status_update",
                    params=params,
                    json=payload,
                    timeout=10.0
                )

                logger.info(f"old_status: {old_status} → new_status: {order['status']}")

                await bot.answer_callback_query(
                    callback.id,
                    text=f"Статус обновлён с {old_status} на {order['status']} ✅"
                )
            else:
                logger.warning(f"Ошибка обновления: {response.status_code}")
                await bot.answer_callback_query(
                    callback.id,
                    text=f"❌ Ошибка обновления: {response.status_code}"
                )

    except Exception as e:
        logger.error(f"Ошибка при обновлении: {e}")
        await bot.answer_callback_query(
            callback.id,
            text="Ошибка при обновлении ❌"
        )
