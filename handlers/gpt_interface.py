from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.prompts import load_prompt
from utils.chatgpt_instance import gpt

router = Router()

DEFAULT_GPT_PROMPT = load_prompt("gpt.txt")


class GPTState(StatesGroup):
    chatting = State()


@router.message(F.text == "/gpt")
async def gpt_start(message: Message, state: FSMContext):
    await state.set_state(GPTState.chatting)
    gpt.set_prompt(DEFAULT_GPT_PROMPT)

    image = FSInputFile("images/gpt.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Закончить", callback_data="start")]
    ])
    await message.answer_photo(
        image,
        caption="💬 Задавай вопросы. Я буду отвечать как ChatGPT.\n\nНажми 🔙 Закончить, чтобы выйти.",
        reply_markup=kb
    )


@router.callback_query(F.data == "gpt")
async def gpt_callback(callback: CallbackQuery, state: FSMContext):
    await gpt_start(callback.message, state)


@router.message(GPTState.chatting)
async def gpt_chatting(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await gpt.add_message(message.text)
        await message.answer(response)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")
