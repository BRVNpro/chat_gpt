from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.chatgpt_instance import gpt

router = Router()

LANGUAGES = {
    "en": "Английский",
    "fr": "Французский",
    "de": "Немецкий",
    "es": "Испанский",
}


class TranslatorStates(StatesGroup):
    choosing_language = State()
    translating = State()


@router.message(F.text == "/translate")
async def translator_start(message: Message, state: FSMContext):
    await state.set_state(TranslatorStates.choosing_language)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"lang:{code}")]
        for code, name in LANGUAGES.items()
    ])
    await message.answer("🌍 Выберите язык для перевода:", reply_markup=kb)


@router.callback_query(F.data == "translate")
async def translate_callback(callback: CallbackQuery, state: FSMContext):
    await translator_start(callback.message, state)


@router.callback_query(F.data.startswith("lang:"))
async def translator_choose_lang(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(":")[1]
    lang_name = LANGUAGES.get(lang_code, "неизвестный язык")

    await state.update_data(lang_code=lang_code)
    await state.set_state(TranslatorStates.translating)

    await callback.message.answer(f"✍️ Отправьте текст для перевода на {lang_name}.")


@router.message(TranslatorStates.translating)
async def translator_process(message: Message, state: FSMContext):
    data = await state.get_data()
    lang_code = data["lang_code"]
    lang_name = LANGUAGES.get(lang_code, "язык")

    user_text = message.text
    prompt = f"Переведи текст на {lang_name}:"

    try:
        result = await gpt.send_question(prompt, user_text)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Сменить язык", callback_data="translate_restart")],
            [InlineKeyboardButton(text="🔙 Закончить", callback_data="start")]
        ])
        await message.answer(result, reply_markup=kb)

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при переводе: {e}")


@router.callback_query(F.data == "translate_restart")
async def translator_restart(callback: CallbackQuery, state: FSMContext):
    await translator_start(callback.message, state)