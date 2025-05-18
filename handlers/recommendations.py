from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.chatgpt_instance import gpt

router = Router()

CATEGORIES = {
    "film": "Фильмы",
    "book": "Книги",
    "music": "Музыка"
}


class RecStates(StatesGroup):
    choosing_category = State()
    entering_genre = State()
    showing_result = State()


@router.callback_query(F.data == "recommend")
async def start_recommend(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(RecStates.choosing_category)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"rec_cat:{code}")]
        for code, cat in CATEGORIES.items()
    ])
    await callback.message.answer("🎬 Выбери категорию рекомендаций:", reply_markup=kb)
    await callback.answer()

@router.message(F.text == "/recommend")
async def recommend_command(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RecStates.choosing_category)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"rec_cat:{code}")]
        for code, cat in CATEGORIES.items()
    ])
    await message.answer("🎬 Выбери категорию рекомендаций:", reply_markup=kb)


@router.callback_query(F.data.startswith("rec_cat:"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[1]
    await state.update_data(category=category, blacklist=[], last_result=None)
    await state.set_state(RecStates.entering_genre)

    await callback.message.answer(f"✏️ Введи жанр для {CATEGORIES[category]}:")
    await callback.answer()


@router.message(RecStates.entering_genre)
async def input_genre(message: Message, state: FSMContext):
    genre = message.text
    data = await state.get_data()
    category = data["category"]

    await state.update_data(genre=genre)
    await send_recommendation(message, state, category, genre)


@router.callback_query(F.data == "rec_dislike")
async def handle_dislike(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    blacklist = data.get("blacklist", [])
    last = data.get("last_result")

    if last:
        blacklist.append(last)

    await state.update_data(blacklist=blacklist)
    await send_recommendation(callback.message, state, data["category"], data["genre"])
    await callback.answer()


@router.callback_query(F.data == "rec_restart")
async def restart(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RecStates.entering_genre)
    await callback.message.answer("✏️ Введи новый жанр:")
    await callback.answer()


@router.callback_query(F.data == "start")
async def end(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✅ Рекомендации завершены. Возвращаюсь в главное меню.")
    await callback.answer()


async def send_recommendation(message: Message, state: FSMContext, category: str, genre: str):
    data = await state.get_data()
    blacklist = data.get("blacklist", [])

    prompt = f"Порекомендуй 3 {CATEGORIES[category].lower()} в жанре '{genre}'. Только названия."
    if blacklist:
        prompt += "\nНе предлагай эти: " + ", ".join(blacklist)

    try:
        result = await gpt.send_question(
            prompt_text="Ты культурный советник. Отвечай коротко и по делу.",
            message_text=prompt
        )

        await state.set_state(RecStates.showing_result)
        await state.update_data(last_result=result.strip())

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🙅 Не нравится", callback_data="rec_dislike")],
            [InlineKeyboardButton(text="🔁 Сменить жанр", callback_data="rec_restart")],
            [InlineKeyboardButton(text="🔙 Закончить", callback_data="start")]
        ])

        await message.answer(f"🎯 Вот мои предложения:\n\n{result.strip()}", reply_markup=kb)

    except Exception as e:
        await message.answer("⚠️ Ошибка при получении рекомендации.")