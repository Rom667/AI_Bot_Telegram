from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# основная клавиатура при вызове /start
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/My_git")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🗑 Очистить историю")],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберете пункт меню'
)

# клавиатура настроек
settings = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌡 Изменить температуру")],
        [KeyboardButton(text="🎭 Изменить роль")],
        [KeyboardButton(text="📊 Мои настройки")],
        [KeyboardButton(text="◀️ Назад")]
    ],
    resize_keyboard=True
)

# клавиатура моего гит при вызове /git
git_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Мой Git hub', url='https://github.com/Romo67')]
    ]
)