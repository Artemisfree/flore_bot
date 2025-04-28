import asyncio
from flore_bot.bot import dp, bot
from flore_bot.callbacks import router as callbacks_router
from flore_bot.handlers import router as handlers_router
from flore_bot.logger import logger


async def main():
    dp.include_router(handlers_router)
    dp.include_router(callbacks_router)
    logger.info("Bot is running...")

    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query"]
    )

if __name__ == "__main__":
    asyncio.run(main())
