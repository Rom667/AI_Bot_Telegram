# импорты библиотек
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from dotenv import load_dotenv

load_dotenv()


# LANGCHAIN импорты
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# импорты из файлов бота
import app.keyboards as kb

# Состояния для FSM
class UserSettings(StatesGroup):
    waiting_for_temperature = State()
    waiting_for_role = State()

# Настройки по умолчанию
DEFAULT_TEMPERATURE = 0.7
DEFAULT_ROLE = "Ты полезный AI-ассистент. Отвечай на русском языке."

# Хранилище настроек пользователей индивидуальные
user_settings = {}  # {user_id: {'temperature': float, 'role': str}}

# Хранилище историй диалогов
histories = {}

def get_user_llm(user_id: int):
    """Создаёт LLM с персональными настройками пользователя"""
    settings = user_settings.get(user_id, {
        'temperature': DEFAULT_TEMPERATURE,
        'role': DEFAULT_ROLE
    })
    
    return ChatGroq(
        groq_api_key=os.getenv('GROQ_API_KEY'),
        model_name="llama-3.3-70b-versatile",
        temperature=settings['temperature']
    )

# имя роутера
router = Router()

# /start
@router.message(CommandStart())
async def cmd_start(message: Message, user_logger):
    user_id = message.from_user.id
    user_logger.log_message(message, action_type="command_start")
    
    # Инициализация настроек для нового пользователя
    if user_id not in user_settings:
        user_settings[user_id] = {
            'temperature': DEFAULT_TEMPERATURE,
            'role': DEFAULT_ROLE
        }
    
    await message.answer(
        f'Привет, {message.from_user.first_name}! 👋\n\n'
        'Я AI-ассистент. Можешь настроить меня под себя!',
        reply_markup=kb.main
    )

@router.message(Command('chatid'))
async def get_chat_id(message: Message):
    await message.answer(
        f"📍 ID этого чата: `{message.chat.id}`\n"
        f"Тип чата: {message.chat.type}",
        parse_mode="Markdown"
    )

# /help
@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer(
        '📖 Доступные команды:\n\n'
        '/start - Начать работу\n'
        '/help - Помощь\n\n'
        'Используй кнопки меню для настройки!'
    )

# Команда /ai для вопросов (работает и в группах, и в личке)
@router.message(Command('ai'))
async def cmd_ai(message: Message, user_logger): #логгер
    # Логируем команду
    user_logger.log_message(message, action_type="command_ai")
    
    user_id = message.from_user.id
    
    # Получаем текст после команды /ai
    command_text = message.text[4:].strip()  # убираем "/ai " и пробелы
    
    if not command_text:
        await message.reply("Использование: /ai ваш вопрос\n\nПример: /ai как дела?")
        return
    
    # Добавление настроек если их нет
    if user_id not in user_settings:
        user_settings[user_id] = {
            'temperature': DEFAULT_TEMPERATURE,
            'role': DEFAULT_ROLE
        }
    
    # Создание истории с системным промптом
    if user_id not in histories:
        role = user_settings[user_id]['role']
        histories[user_id] = [SystemMessage(content=role)]
    
    # Добавление сообщения пользователя
    histories[user_id].append(HumanMessage(content=command_text))
    
    try:
        # Показываем что бот думает
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # Получаем персональную LLM
        llm = get_user_llm(user_id)
        
        # Получаем ответ
        response = llm.invoke(histories[user_id])
        
        # Добавляем ответ в историю
        histories[user_id].append(AIMessage(content=response.content))
        
        # Отправляем ответ
        await message.reply(response.content)
        
        # Ограничиваем историю
        if len(histories[user_id]) > 21:
            histories[user_id] = [histories[user_id][0]] + histories[user_id][-20:]
    
    except Exception as e:
        await message.reply(f'❌ Ошибка: {str(e)}')

@router.message(Command("My_git"))
async def my_git(message: Message):
    await message.answer(f"It is my git", reply_markup=kb.git_button)

# Кнопка "⚙️ Настройки"
@router.message(F.text == '⚙️ Настройки')
async def show_settings(message: Message):
    await message.answer('⚙️ Выберите настройку:', reply_markup=kb.settings)

# Кнопка "◀️ Назад"
@router.message(F.text == '◀️ Назад')
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Главное меню:', reply_markup=kb.main)

# Кнопка "📊 Мои настройки"
@router.message(F.text == '📊 Мои настройки')
async def my_settings(message: Message):
    user_id = message.from_user.id
    settings = user_settings.get(user_id, {
        'temperature': DEFAULT_TEMPERATURE,
        'role': DEFAULT_ROLE
    })
    
    await message.answer(
        f'📊 Ваши текущие настройки:\n\n'
        f'🌡 Температура: {settings["temperature"]}\n'
        f'🎭 Роль: {settings["role"][:100]}...'
    )

# Кнопка "🌡 Изменить температуру"
@router.message(F.text == '🌡 Изменить температуру')
async def change_temperature(message: Message, state: FSMContext):
    await state.set_state(UserSettings.waiting_for_temperature)
    await message.answer(
        '🌡 Введите температуру от 0.0 до 1.0:\n\n'
        '0.0 - точные ответы\n'
        '0.5 - сбалансированные\n'
        '1.0 - креативные ответы\n\n'
        'Или напишите "отмена"'
    )

@router.message(UserSettings.waiting_for_temperature)
async def process_temperature(message: Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer('Отменено', reply_markup=kb.settings)
        return
    
    try:
        temp = float(message.text)
        if 0.0 <= temp <= 1.0:
            user_id = message.from_user.id
            if user_id not in user_settings:
                user_settings[user_id] = {'temperature': temp, 'role': DEFAULT_ROLE}
            else:
                user_settings[user_id]['temperature'] = temp
            
            await state.clear()
            await message.answer(
                f'✅ Температура установлена: {temp}',
                reply_markup=kb.settings
            )
        else:
            await message.answer('❌ Число должно быть от 0.0 до 1.0')
    except ValueError:
        await message.answer('❌ Введите число! Например: 0.7')

# Кнопка "🎭 Изменить роль"
@router.message(F.text == '🎭 Изменить роль')
async def change_role(message: Message, state: FSMContext):
    await state.set_state(UserSettings.waiting_for_role)
    await message.answer(
        '🎭 Введите системный промпт (роль ассистента):\n\n'
        'Например:\n'
        '- "Ты программист Python"\n'
        '- "Ты дружелюбный помощник"\n'
        '- "Ты строгий учитель"\n\n'
        'Или напишите "отмена"'
    )

@router.message(UserSettings.waiting_for_role)
async def process_role(message: Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer('Отменено', reply_markup=kb.settings)
        return
    
    user_id = message.from_user.id
    if user_id not in user_settings:
        user_settings[user_id] = {'temperature': DEFAULT_TEMPERATURE, 'role': message.text}
    else:
        user_settings[user_id]['role'] = message.text
    
    # Очищаем историю при смене роли
    if user_id in histories:
        histories[user_id] = []
    
    await state.clear()
    await message.answer(
        f'✅ Роль установлена!\n\n{message.text}',
        reply_markup=kb.settings
    )

# Кнопка "🗑 Очистить историю"
@router.message(F.text == '🗑 Очистить историю')
async def clear_history(message: Message):
    user_id = message.from_user.id
    histories[user_id] = []
    await message.answer('🗑 История очищена!', reply_markup=kb.main)

# ОБРАБОТЧИК ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ (должен быть в конце!)
@router.message(F.text)
async def handle_text(message: Message, state: FSMContext, user_logger):
    # Логируем сообщение
    user_logger.log_message(message, action_type="text_message")
    
    # Проверяем, не находимся ли мы в состоянии ожидания настроек
    current_state = await state.get_state()
    if current_state is not None:
        return
    
    user_id = message.from_user.id
    
    # Пропускаем команды и кнопки клавиатуры
    if message.text.startswith('/'):
        return
    
    buttons = ['💬Чат с AI', '⚙️ Настройки', '🗑 Очистить историю', 
                '◀️ Назад', '📊 Мои настройки',
                '🌡 Изменить температуру', '🎭 Изменить роль', 'My_git']
    if message.text in buttons:
        return
    
    # Инициализация настроек если их нет
    if user_id not in user_settings:
        user_settings[user_id] = {
            'temperature': DEFAULT_TEMPERATURE,
            'role': DEFAULT_ROLE
        }
    
    # Создаём историю с системным промптом
    if user_id not in histories:
        role = user_settings[user_id]['role']
        histories[user_id] = [SystemMessage(content=role)]
    
    # Добавляем сообщение пользователя
    histories[user_id].append(HumanMessage(content=message.text))
    
    try:
        # Получаем персональную LLM
        llm = get_user_llm(user_id)
        
        # Получаем ответ
        response = llm.invoke(histories[user_id])
        
        # Добавляем ответ в историю
        histories[user_id].append(AIMessage(content=response.content))
        
        # Отправляем ответ
        await message.answer(response.content)
        
        # Ограничиваем историю (1 system + 20 сообщений)
        if len(histories[user_id]) > 21:
            histories[user_id] = [histories[user_id][0]] + histories[user_id][-20:]
    
    except Exception as e:
        await message.answer(f'❌ Ошибка: {str(e)}')