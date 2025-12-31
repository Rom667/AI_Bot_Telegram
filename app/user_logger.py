import sqlite3
from datetime import datetime
from aiogram.types import Message, CallbackQuery

class UserLogger:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def log_message(self, message: Message, action_type: str = "message"):
        """Логирование сообщения пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_actions 
            (user_id, username, first_name, last_name, action_type, message_text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            action_type,
            message.text or message.caption or "[медиа]",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        conn.close()
    
    def log_callback(self, callback: CallbackQuery, action_type: str = "callback"):
        """Логирование нажатия кнопки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_actions 
            (user_id, username, first_name, last_name, action_type, message_text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            callback.from_user.id,
            callback.from_user.username,
            callback.from_user.first_name,
            callback.from_user.last_name,
            action_type,
            callback.data,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        conn.close()