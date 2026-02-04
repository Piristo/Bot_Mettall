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


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Старт", callback_data="start_menu")]
        ]
    )


def get_year_paging_keyboard(
    year: int,
    concert_page: int,
    concert_total_pages: int,
    interview_page: int,
    interview_total_pages: int
) -> InlineKeyboardMarkup:
    rows = []

    concert_row = []
    if concert_total_pages > 0:
        if concert_page > 1:
            concert_row.append(InlineKeyboardButton(text="🎸 ⬅️", callback_data=f"year_{year}_c{concert_page-1}_i{interview_page}"))
        concert_row.append(InlineKeyboardButton(text=f"🎸 {concert_page}/{concert_total_pages}", callback_data="page_info"))
        if concert_page < concert_total_pages:
            concert_row.append(InlineKeyboardButton(text="🎸 ➡️", callback_data=f"year_{year}_c{concert_page+1}_i{interview_page}"))
    if concert_row:
        rows.append(concert_row)

    interview_row = []
    if interview_total_pages > 0:
        if interview_page > 1:
            interview_row.append(InlineKeyboardButton(text="🎤 ⬅️", callback_data=f"year_{year}_c{concert_page}_i{interview_page-1}"))
        interview_row.append(InlineKeyboardButton(text=f"🎤 {interview_page}/{interview_total_pages}", callback_data="page_info"))
        if interview_page < interview_total_pages:
            interview_row.append(InlineKeyboardButton(text="🎤 ➡️", callback_data=f"year_{year}_c{concert_page}_i{interview_page+1}"))
    if interview_row:
        rows.append(interview_row)

    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_tour_paging_keyboard(tour_name: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows = []

    tour_slug = tour_name.replace(" ", "_")
    row = []
    if page > 1:
        row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"tourpage_{page-1}_{tour_slug}"))
    row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="page_info"))
    if page < total_pages:
        row.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"tourpage_{page+1}_{tour_slug}"))
    rows.append(row)

    rows.append([InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)
