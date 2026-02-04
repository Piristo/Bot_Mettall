from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import AsyncSessionLocal
from database.repository import VideoRepository
from utils.formatters import Formatter
from bot.keyboards.inline import get_concerts_keyboard, get_interviews_keyboard, get_archive_keyboard, get_year_paging_keyboard, get_tour_paging_keyboard
from bot.constants import CONTENT_TYPE_CONCERT, CONTENT_TYPE_INTERVIEW, RESULTS_PER_PAGE

router = Router()

@router.callback_query(F.data.startswith("concerts_"))
async def callback_concerts(callback: CallbackQuery):
    parts = callback.data.split("_")
    page = int(parts[1]) if len(parts) > 1 else 1
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        offset = (page - 1) * RESULTS_PER_PAGE
        videos = await repo.get_videos(content_type=CONTENT_TYPE_CONCERT, sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=offset)
        count = await repo.get_videos_count(content_type=CONTENT_TYPE_CONCERT)
    
    if videos:
        text = f"🎸 **Концерты Metallica** (страница {page})\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        total_pages = (count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        await callback.message.edit_text(text, reply_markup=get_concerts_keyboard(page, total_pages), parse_mode="Markdown")
    else:
        await callback.message.edit_text("Концерты не найдены", reply_markup=get_concerts_keyboard(page, 1))
    
    await callback.answer()

@router.callback_query(F.data.startswith("interviews_"))
async def callback_interviews(callback: CallbackQuery):
    parts = callback.data.split("_")
    page = int(parts[1]) if len(parts) > 1 else 1
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        offset = (page - 1) * RESULTS_PER_PAGE
        videos = await repo.get_videos(content_type=CONTENT_TYPE_INTERVIEW, sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=offset)
        count = await repo.get_videos_count(content_type=CONTENT_TYPE_INTERVIEW)
    
    if videos:
        text = f"🎤 **Интервью Metallica** (страница {page})\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        total_pages = (count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        await callback.message.edit_text(text, reply_markup=get_interviews_keyboard(page, total_pages), parse_mode="Markdown")
    else:
        await callback.message.edit_text("Интервью не найдены", reply_markup=get_interviews_keyboard(page, 1))
    
    await callback.answer()

@router.callback_query(F.data.startswith("archive_"))
async def callback_archive(callback: CallbackQuery):
    parts = callback.data.split("_")
    page = int(parts[1]) if len(parts) > 1 else 1
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        offset = (page - 1) * RESULTS_PER_PAGE
        videos = await repo.get_videos(sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=offset)
        count = await repo.get_videos_count()
    
    if videos:
        text = f"📦 **Архив Metallica** (страница {page})\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        total_pages = (count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        await callback.message.edit_text(text, reply_markup=get_archive_keyboard(page, total_pages), parse_mode="Markdown")
    else:
        await callback.message.edit_text("Записи не найдены", reply_markup=get_archive_keyboard(page, 1))
    
    await callback.answer()


@router.callback_query(F.data.startswith("year_"))
async def callback_year(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer()
        return

    year = int(parts[1])
    concert_page = 1
    interview_page = 1

    for part in parts[2:]:
        if part.startswith("c"):
            concert_page = int(part[1:])
        elif part.startswith("i"):
            interview_page = int(part[1:])

    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        concert_offset = (concert_page - 1) * RESULTS_PER_PAGE
        interview_offset = (interview_page - 1) * RESULTS_PER_PAGE

        concerts = await repo.get_videos(content_type=CONTENT_TYPE_CONCERT, year=year, sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=concert_offset)
        interviews = await repo.get_videos(content_type=CONTENT_TYPE_INTERVIEW, year=year, sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=interview_offset)
        concerts_count = await repo.get_videos_count(content_type=CONTENT_TYPE_CONCERT, year=year)
        interviews_count = await repo.get_videos_count(content_type=CONTENT_TYPE_INTERVIEW, year=year)

    total_count = concerts_count + interviews_count
    text = f"📅 **Metallica {year}** ({total_count} записей)\n\n"

    if concerts:
        text += f"🎸 **Концерты** ({concerts_count})\n\n"
        for video in concerts:
            text += Formatter.format_video_card(video) + "\n"

    if interviews:
        text += f"🎤 **Интервью** ({interviews_count})\n\n"
        for video in interviews:
            text += Formatter.format_video_card(video) + "\n"

    concert_total_pages = (concerts_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE if concerts_count else 0
    interview_total_pages = (interviews_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE if interviews_count else 0

    keyboard = get_year_paging_keyboard(year, concert_page, concert_total_pages, interview_page, interview_total_pages)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("tourpage_"))
async def callback_tour_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer()
        return

    page = int(parts[1])
    tour_name = " ".join(parts[2:]).replace("_", " ")

    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        offset = (page - 1) * RESULTS_PER_PAGE
        videos = await repo.get_videos(tour_name=tour_name, sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=offset)
        count = await repo.get_videos_count(tour_name=tour_name)

    if videos:
        text = f"🎫 **{tour_name}** ({count} записей)\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"

        total_pages = (count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        keyboard = get_tour_paging_keyboard(tour_name, page, total_pages)
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await callback.message.edit_text(f"😔 Концерты тура \"{tour_name}\" не найдены", reply_markup=get_tour_paging_keyboard(tour_name, 1, 1))

    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def callback_back(callback: CallbackQuery):
    from bot.keyboards.reply import get_main_keyboard
    await callback.message.edit_text("Возврат в главное меню", reply_markup=None)
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "start_menu")
async def callback_start_menu(callback: CallbackQuery):
    from bot.keyboards.reply import get_main_keyboard
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("filter_"))
async def callback_filter(callback: CallbackQuery):
    filter_type = callback.data.split("_")[1]
    
    if filter_type == "hd":
        quality_filter = "HD"
    elif filter_type == "official":
        quality_filter = "OFFICIAL"
    elif filter_type == "complete":
        quality_filter = "COMPLETE"
    else:
        quality_filter = None
    
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        offset = 0
        videos = await repo.get_videos(content_type=CONTENT_TYPE_CONCERT, quality_filter=quality_filter, sort_by="date", sort_order="asc", limit=RESULTS_PER_PAGE, offset=offset)
        count = await repo.get_videos_count(content_type=CONTENT_TYPE_CONCERT, quality_filter=quality_filter)
    
    if videos:
        filter_name = quality_filter if quality_filter else "Все"
        text = f"🎸 **Концерты Metallica** (фильтр: {filter_name})\n\n"
        for video in videos:
            text += Formatter.format_video_card(video) + "\n"
        
        total_pages = (count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        await callback.message.edit_text(text, reply_markup=get_concerts_keyboard(page=1, total_pages=total_pages), parse_mode="Markdown")
    else:
        filter_name = quality_filter if quality_filter else "Все"
        await callback.message.edit_text(f"Концерты с фильтром '{filter_name}' не найдены", reply_markup=get_concerts_keyboard(page=1, total_pages=1))
    
    await callback.answer()
