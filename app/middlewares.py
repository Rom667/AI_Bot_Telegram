from aiogram import BaseMiddleware
from aiogram.types import Message
from app.config import ALLOWED_USERS, ALLOWED_GROUPS  # <-- оба импорта

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        # Если это группа - проверяем разрешённые группы
        if event.chat.type in ['group', 'supergroup']:
            if event.chat.id not in ALLOWED_GROUPS:
                return  # Игнорируем чужие группы
            return await handler(event, data)
        
        # Если это личка - проверяем белый список друзей
        if event.from_user.id not in ALLOWED_USERS:
            await event.answer("⛔ Доступ запрещён. Бот только для друзей!")
            return
        
        return await handler(event, data)