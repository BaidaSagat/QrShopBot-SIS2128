import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.BotHandlers import router
from DB.tables import async_main
async def main(): # Main function (bot initialization and polling)
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__': # Run main function and also Logging to a file
    logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:  # When we press Ctrl+C, cancel all tasks
        print('Exit')