import sqlite3

def init_database(db_path: str = "bot.db"):
    """Создание таблиц при запуске бота"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Таблица для системных логов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            module TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
        ON logs(timestamp)
    """)
    
    # Таблица для логов пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            action_type TEXT NOT NULL,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_actions_user_id 
        ON user_actions(user_id)
    """)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")