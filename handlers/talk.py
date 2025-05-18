from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from states.talk_states import TalkStates
from utils.chatgpt_instance import gpt
from utils.prompts import load_prompt

router = Router()

CHARACTERS = {
    "cobain": ("Курт Кобейн 🎸", "talk_cobain.txt", "talk_cobain.jpg"),
    "queen": ("Елизавета II 👑", "talk_queen.txt", "talk_queen.jpg"),
    "tolkien": ("Джон Толкиен 📖", "talk_tolkien.txt", "talk_tolkien.jpg"),
    "nietzsche": ("Фридрих Ницше 🧠", "talk_nietzsche.txt", "talk_nietzsche.jpg"),
    "hawking": ("Стивен Хокинг 🔬", "talk_hawking.txt", "talk_hawking.jpg"),
}


@router.message(F.text == "/talk")
async def talk_start(message: Message, state: FSMContext):
    await state.set_state(TalkStates.selecting_character)

    image = FSInputFile("images/talk.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=desc, callback_data=f"talk_{code}")]
        for code, (desc, _, _) in CHARACTERS.items()
    ])

    await message.answer_photo(image, caption="👤 Выбери личность, с которой хочешь поговорить:", reply_markup=kb)


@router.callback_query(F.data == "talk")
async def talk_callback(callback: CallbackQuery, state: FSMContext):
    await talk_start(callback.message, state)


@router.callback_query(F.data.startswith("talk_"))
async def select_character(callback: CallbackQuery, state: FSMContext):
    char_code = callback.data.split("_")[1]
    char_info = CHARACTERS.get(char_code)

    if not char_info:
        return await callback.message.answer("❗ Личность не найдена.")

    char_name, prompt_file, image_file = char_info
    prompt_text = load_prompt(prompt_file)

    gpt.set_prompt(prompt_text)
    await state.set_state(TalkStates.chatting)

    image = FSInputFile(f"images/{image_file}")
    await callback.message.answer_photo(
        image,
        caption=f"🗣 Ты выбрал: {char_name}\nТеперь можешь писать, и он будет отвечать.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔙 Закончить", callback_data="start")]]
        )
    )


@router.message(TalkStates.chatting)
async def talk_chat(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await gpt.add_message(message.text)
        await message.answer(response)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка диалога: {e}")
