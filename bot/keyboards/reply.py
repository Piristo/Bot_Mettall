from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎸 Концерты"),
                KeyboardButton(text="🎤 Интервью")
            ],
            [
                KeyboardButton(text="📦 Архив"),
                KeyboardButton(text="🔄 Обновить")
            ],
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="📅 По годам")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def get_search_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 Искать ещё")
            ],
            [
                KeyboardButton(text="🔙 Назад в меню")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
