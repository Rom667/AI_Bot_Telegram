from app.database import init_database
from app.user_logger import UserLogger
from aiogram import Bot, Dispatcher
from app.handlers import router
from dotenv import load_dotenv
import os
import logging
import asyncio
from app.middlewares import AuthMiddleware

load_dotenv()

async def main():
    # Инициализация БД и логгера ПЕРЕД запуском polling
    DB_PATH = "bot.db"
    init_database(DB_PATH)
    user_logger = UserLogger(DB_PATH)
    
    # Создаем bot и dispatcher
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()
    
    # проверка доступа:
    dp.message.middleware(AuthMiddleware())

    # Передаем user_logger в диспетчер
    dp.workflow_data.update({"user_logger": user_logger})
    
    # Подключаем роутер
    dp.include_router(router)
    
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
        