from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.constants import RESULTS_PER_PAGE

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

def get_concerts_keyboard(page: int = 1, total_pages: int = 1, quality_filter: str = None) -> InlineKeyboardMarkup:
    buttons = []
    
    row1 = []
    if page > 1:
        row1.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"concerts_{page-1}"))
    row1.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="page_info"))
    if page < total_pages:
        row1.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"concerts_{page+1}"))
    
    row2 = [
        InlineKeyboardButton(text="⭐ HD", callback_data="filter_hd"),
        InlineKeyboardButton(text="📺 OFFICIAL", callback_data="filter_official"),
        InlineKeyboardButton(text="✅ COMPLETE", callback_data="filter_complete")
    ]
    
    row3 = [
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3])
    return keyboard

def get_interviews_keyboard(page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    buttons = []
    
    row1 = []
    if page > 1:
        row1.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"interviews_{page-1}"))
    row1.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="page_info"))
    if page < total_pages:
        row1.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"interviews_{page+1}"))
    
    row2 = [
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    return keyboard

def get_archive_keyboard(page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    row1 = []
    if page > 1:
        row1.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"archive_{page-1}"))
    row1.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="page_info"))
    if page < total_pages:
        row1.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"archive_{page+1}"))
    
    row2 = [
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2])
    return keyboard

def get_tours_keyboard(tours: list) -> InlineKeyboardMarkup:
    buttons = []
    
    for tour in tours:
        buttons.append([InlineKeyboardButton(text=tour, callback_data=f"tour_{tour}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_years_keyboard(years: list) -> InlineKeyboardMarkup:
    buttons = []
    
    for year in years:
        buttons.append([InlineKeyboardButton(text=str(year), callback_data=f"year_{year}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
