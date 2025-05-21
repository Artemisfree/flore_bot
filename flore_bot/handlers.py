from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import httpx
from flore_bot.bot import bot, ORDER_STATUSES, URL, generate_status_buttons
from flore_bot.logger import logger

router = Router()


class SearchOrderState(StatesGroup):
    waiting_for_id = State()


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Find order")],
        [KeyboardButton(text="ℹ️ Help")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я бот для управления заказами.\n\n"
        "Нажмите на кнопку или используйте команды ниже:\n"
        "«ℹ️ Help» или /help - Справка по командам\n"
        "«🔍 Find order» или /find <order_id> - Найти заказ\n",
        reply_markup=main_menu
    )


@router.message(Command("help"))
async def help_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "ℹ️ Справка по боту:\n"
        "🔍 Нажмите «Find order» или введите команду /find <order_id>,\n"
        "чтобы найти заказ по ID и изменить его статус.",
        reply_markup=main_menu
    )


@router.message(lambda m: m.text == "ℹ️ Help")
async def help_button(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "ℹ️ Справка по боту:\n"
        "🔍 Нажмите «Find order», чтобы начать поиск.\n"
        "Или введите команду /find <order_id>.",
        reply_markup=main_menu
    )


@router.message(lambda m: m.text == "🔍 Find order")
async def find_button(message: types.Message, state: FSMContext):
    await state.set_state(SearchOrderState.waiting_for_id)
    await message.answer(
        "❗️ Введите ID заказа \n"
        "Пример:\n"
        "`68109a9cea615abe59283311`",
        parse_mode="Markdown",
        reply_markup=main_menu
    )


@router.message(SearchOrderState.waiting_for_id)
async def process_order_id(message: types.Message, state: FSMContext):
    order_id = message.text.strip()
    await message.answer("🔍 Ищу заказ…", reply_markup=main_menu)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{URL}/api/orders/{order_id}",
                headers={"is-admin": "true"},
                timeout=5.0
            )
        if resp.status_code == 200:
            order = resp.json()
            text = (
                f"🛒 Order #{order['_id']}\n"
                f"👤 Customer: {order['customerName']}\n"
                f"📧 Email: {order['email']}\n"
                f"📱 Phone: {order['phone']}\n"
                f"📍 Address: {order['address']}\n"
                f"📝 Notes: {order['notes']}\n"
                f"💰 Total: {order['totalAmount']}$\n"
                f"📦 Status: {order['status']}\n"
            )

            for item in order.get("items", []):
                text += f"🪻 Title: {item.get('title', 'Item')}\n"
                text += f"📏 Size: {item.get('size', '')}\n"

            first_image_url = None
            for item in order.get("items", []):
                url = item.get("imageUrl")
                if url and url.startswith("http"):
                    first_image_url = url
                    break

            if first_image_url:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=first_image_url,
                    caption=text,
                    reply_markup=generate_status_buttons(order["_id"])
                )
            else:
                await message.answer(
                    text=text,
                    reply_markup=generate_status_buttons(order["_id"])
                )

            # await message.answer(text, reply_markup=generate_status_buttons(order["_id"]))
        else:
            logger.error(f"❌ Заказ не найден. ID: {order_id}")
            await message.answer("❌ Заказ не найден.", reply_markup=main_menu)

    except Exception as e:
        logger.error(f"Ошибка при поиске заказа {order_id}: {e}")
        await message.answer("❌ Не удалось получить данные заказа.", reply_markup=main_menu)

    # 4) Сбрасываем состояние
    await state.clear()


# 5) Сохраняем старую команду /find для тех, кто предпочитает slash
@router.message(Command("find"))
async def cmd_find_order(message: types.Message, state: FSMContext):
    await state.clear()
    parts = (message.text or "").strip().split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        return await message.reply(
            "❗️ Укажите ID заказа после команды.\n"
            "Пример: `/find 68109a9cea615abe59283311`",
            parse_mode="Markdown",
            reply_markup=main_menu
        )
    # просто перенаправляем на общий обработчик
    message.text = parts[1].strip()
    await process_order_id(message, state)


@router.callback_query(lambda c: c.data and c.data.startswith("set_status:"))
async def handle_status_change(callback: types.CallbackQuery):
    _, order_id, new_status_code = callback.data.split(":")
    js_status = ORDER_STATUSES[new_status_code]

    await bot.answer_callback_query(callback.id, text="Обрабатываю...")

    try:
        async with httpx.AsyncClient() as client:
            # 1) Получаем старый статус
            old_resp = await client.get(
                f"{URL}/api/orders/{order_id}",
                headers={"is-admin": "true"},
            )
            old_order = old_resp.json()
            old_status = old_order["status"]

            # 2) Обновляем статус
            patch_resp = await client.patch(
                f"{URL}/api/orders/{order_id}/status",
                json={"status": js_status},
                headers={"is-admin": "true"}
            )
            logger.info(f"PATCH status code: {patch_resp.status_code}")
            logger.info(f"Response text: {patch_resp.text}")

            if patch_resp.status_code != 200:
                await bot.answer_callback_query(
                    callback.id,
                    text=f"❌ Ошибка обновления: {patch_resp.status_code}"
                )
                return

            # 3) Получаем обновлённый заказ
            get_resp = await client.get(
                f"{URL}/api/orders/{order_id}",
                headers={"is-admin": "true"}
            )
            order = get_resp.json()

            # 4) Уведомляем сервис через FastAPI
            payload = {
                "orderId":      order["_id"],
                "customerName": order["customerName"],
                "totalAmount":  order["totalAmount"],
                "email":        order["email"],
                "phone":        order["phone"],
                "address":      order["address"],
                "notes":        order["notes"],
                "items":        order["items"],
                "status":       order["status"],
            }
            params = {"previousStatus": old_status}
            await client.post(
                f"{URL}/notify_status_update",
                json=payload,
                params=params,
                timeout=10.0
            )

            logger.info(f"{old_status} → {order['status']}")

            # 5) Подтверждаем callback_query
            await bot.answer_callback_query(
                callback.id,
                text=f"Статус обновлён с {old_status} на {order['status']} ✅"
            )

    except Exception as e:
        logger.error(f"Ошибка при обновлении: {e}")
        await bot.answer_callback_query(
            callback.id,
            text="Ошибка при обновлении ❌"
        )
