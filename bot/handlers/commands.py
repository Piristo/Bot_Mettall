from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from database.models import AsyncSessionLocal
from database.repository import VideoRepository, SyncStatusRepository
from utils.formatters import Formatter
from bot.keyboards.inline import get_concerts_keyboard, get_interviews_keyboard, get_archive_keyboard, get_tours_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.constants import CONTENT_TYPE_CONCERT, CONTENT_TYPE_INTERVIEW

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "🎸 **Metallica Archive Bot**\n\n"
        "Добро пожаловать в архив лучших концертов и интервью Metallica!\n\n"
        "📚 **Доступные команды:**\n"
        "🎸 /concerts - Полные концерты\n"
        "🎤 /interviews - Полные интервью\n"
        "📦 /archive - Хронологический архив\n"
        "🎫 /tour [название] - Концерты тура\n"
        "📅 /year [год] - Записи за год\n"
        "🔄 /refresh - Обновить базу\n"
        "📊 /stats - Статистика\n\n"
        "Используйте кнопки ниже для быстрого доступа:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@router.message(Command("concerts"))
async def cmd_concerts(message: Message):
    await message.answer("🎸 Загрузка концертов...", reply_markup=None)
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        videos = await repo.get_videos(content_type=CONTENT_TYPE_CONCERT, limit=10, offset=0)
        count = await repo.get_videos_count(content_type=CONTENT_TYPE_CONCERT)
    
    if videos:
        text = f"🎸 **Полные концерты Metallica** ({count} всего)\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        await message.answer(text, reply_markup=get_concerts_keyboard(page=1, total_pages=(count + 9) // 10), parse_mode="Markdown")
    else:
        await message.answer(Formatter.format_no_results("concert"), reply_markup=get_main_keyboard())

@router.message(Command("interviews"))
async def cmd_interviews(message: Message):
    await message.answer("🎤 Загрузка интервью...", reply_markup=None)
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        videos = await repo.get_videos(content_type=CONTENT_TYPE_INTERVIEW, limit=10, offset=0)
        count = await repo.get_videos_count(content_type=CONTENT_TYPE_INTERVIEW)
    
    if videos:
        text = f"🎤 **Полные интервью Metallica** ({count} всего)\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        await message.answer(text, reply_markup=get_interviews_keyboard(page=1, total_pages=(count + 9) // 10), parse_mode="Markdown")
    else:
        await message.answer(Formatter.format_no_results("interview"), reply_markup=get_main_keyboard())

@router.message(Command("archive"))
async def cmd_archive(message: Message):
    await message.answer("📦 Загрузка архива...", reply_markup=None)
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        videos = await repo.get_videos(limit=10, offset=0)
        count = await repo.get_videos_count()
    
    if videos:
        text = f"📦 **Архив Metallica** ({count} всего)\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        await message.answer(text, reply_markup=get_archive_keyboard(page=1, total_pages=(count + 9) // 10), parse_mode="Markdown")
    else:
        await message.answer(Formatter.format_no_results("archive"), reply_markup=get_main_keyboard())

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        concerts = await repo.get_videos_count(content_type=CONTENT_TYPE_CONCERT)
        interviews = await repo.get_videos_count(content_type=CONTENT_TYPE_INTERVIEW)
        total = await repo.get_videos_count()
    
    await message.answer(Formatter.format_stats(concerts, interviews, total), reply_markup=get_main_keyboard())

@router.message(Command("refresh"))
async def cmd_refresh(message: Message):
    await message.answer("🔄 Запускаю обновление базы...\n\nЭто может занять несколько минут. Пожалуйста, подождите.", reply_markup=get_main_keyboard())
    await message.answer("⚠️ Функция обновления пока недоступна. Требуется настройка YouTube API ключа.", reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🎸 **Metallica Archive Bot - Помощь**\n\n"
        "📚 **Команды:**\n"
        "/concerts - Показать полные концерты\n"
        "/interviews - Показать полные интервью\n"
        "/archive - Показать весь архив\n"
        "/tour [название] - Фильтр по туру\n"
        "/year [год] - Фильтр по году\n"
        "/search [запрос] - Поиск\n"
        "/refresh - Обновить базу\n"
        "/stats - Статистика\n"
        "/help - Эта справка\n\n"
        "🎯 **Советы:**\n"
        "- Используйте кнопки для навигации\n"
        "- Нажимайте на ссылки для просмотра видео\n"
        "- Обновляйте базу для новых записей"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@router.message()
async def cmd_default(message: Message):
    if message.text.startswith("/tour"):
        parts = message.text.split()
        if len(parts) > 1:
            tour_name = " ".join(parts[1:])
            await show_tour(message, tour_name)
        else:
            await message.answer("Укажите название тура: /tour [название]", reply_markup=get_main_keyboard())
    elif message.text.startswith("/year"):
        parts = message.text.split()
        if len(parts) > 1:
            try:
                year = int(parts[1])
                await show_year(message, year)
            except ValueError:
                await message.answer("Укажите корректный год: /year [1981-2026]", reply_markup=get_main_keyboard())
        else:
            await message.answer("Укажите год: /year [1981-2026]", reply_markup=get_main_keyboard())
    else:
        await message.answer("Неизвестная команда. Используйте /help для списка команд.", reply_markup=get_main_keyboard())

async def show_tour(message: Message, tour_name: str):
    await message.answer(f"🎫 Поиск тура: {tour_name}...")
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        videos = await repo.get_videos(tour_name=tour_name, limit=10, offset=0)
        count = await repo.get_videos_count(tour_name=tour_name)
    
    if videos:
        text = f"🎫 **{tour_name}** ({count} записей)\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer(f"😔 Концерты тура \"{tour_name}\" не найдены", reply_markup=get_main_keyboard())

async def show_year(message: Message, year: int):
    if year < 1981 or year > 2026:
        await message.answer("Год должен быть между 1981 и 2026", reply_markup=get_main_keyboard())
        return
    
    await message.answer(f"📅 Поиск записей за {year} год...")
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        videos = await repo.get_videos(year=year, limit=10, offset=0)
        count = await repo.get_videos_count(year=year)
    
    if videos:
        text = f"📅 **Metallica {year}** ({count} записей)\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer(f"😔 Записи за {year} год не найдены", reply_markup=get_main_keyboard())
