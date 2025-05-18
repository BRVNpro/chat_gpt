from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from keyboards.inline import fact_buttons
from utils.chatgpt_instance import gpt
from utils.prompts import load_prompt

router = Router()

RANDOM_FACT_PROMPT = load_prompt("random.txt")


@router.message(F.text == "/random")
async def random_fact_command(message: Message):
    image = FSInputFile("images/random.jpg")
    await message.answer_photo(photo=image, caption="🔍 Думаю над фактом...")

    try:
        response = await gpt.send_question(RANDOM_FACT_PROMPT, "")
        await message.answer(response, reply_markup=fact_buttons())

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при получении факта: {e}")


@router.callback_query(F.data == "random")
async def random_fact_callback(callback: CallbackQuery):
    image = FSInputFile("images/random.jpg")
    await callback.message.answer_photo(photo=image, caption="🔍 Думаю над фактом...")

    try:
        response = await gpt.send_question(RANDOM_FACT_PROMPT, "")
        await callback.message.answer(response, reply_markup=fact_buttons())

    except Exception as e:
        await callback.message.answer(f"⚠️ Ошибка при получении факта: {e}")