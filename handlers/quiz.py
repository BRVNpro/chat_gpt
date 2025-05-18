from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from states.quiz_states import QuizStates
from utils.chatgpt_instance import gpt
from utils.prompts import load_prompt

router = Router()

TOPICS = {
    "quiz_prog": "Программирование",
    "quiz_math": "Математика",
    "quiz_biology": "Биология"
}

BASE_PROMPT = load_prompt("quiz.txt")


@router.message(F.text == "/quiz")
async def quiz_start(message: Message, state: FSMContext):
    await state.set_state(QuizStates.selecting_topic)

    image = FSInputFile("images/quiz.jpg")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=code)] for code, name in TOPICS.items()
    ])
    await message.answer_photo(image, caption="🎓 Выбери тему для квиза:", reply_markup=kb)


@router.callback_query(F.data == "quiz")
async def quiz_callback(callback: CallbackQuery, state: FSMContext):
    await quiz_start(callback.message, state)


@router.callback_query(F.data.in_(TOPICS.keys()))
async def select_topic(callback: CallbackQuery, state: FSMContext):
    topic_code = callback.data
    await state.update_data(topic=topic_code, last_topic=topic_code, score=0, total=0)
    await ask_question(callback.message, state, topic_code)


async def ask_question(message: Message, state: FSMContext, topic_code: str):
    await state.set_state(QuizStates.waiting_for_answer)

    if topic_code == "quiz_more":
        data = await state.get_data()
        topic_code = data.get("last_topic", "quiz_prog")

    try:
        question = await gpt.send_question(BASE_PROMPT, topic_code)
        await state.update_data(current_question=question)
        await message.answer(f"❓ Вопрос:\n{question}")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при получении вопроса: {e}")


@router.message(QuizStates.waiting_for_answer)
async def process_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    user_answer = message.text
    question = data["current_question"]
    topic = data.get("topic", "quiz_prog")

    try:
        result = await gpt.send_question(
            prompt_text=BASE_PROMPT,
            message_text=f"Вопрос: {question}\nОтвет: {user_answer}"
        )

        is_correct = result.strip().lower().startswith("правильно!")
        score = data.get("score", 0) + int(is_correct)
        total = data.get("total", 0) + 1

        await state.update_data(score=score, total=total)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Следующий вопрос", callback_data="quiz_more")],
            [InlineKeyboardButton(text="📚 Сменить тему", callback_data="quiz_change_topic")],
            [InlineKeyboardButton(text="🔙 Закончить", callback_data="start")]
        ])

        await message.answer(f"{result}\n\n📊 Счёт: {score}/{total}", reply_markup=kb)

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при проверке ответа: {e}")


@router.callback_query(F.data == "quiz_more")
async def quiz_more(callback: CallbackQuery, state: FSMContext):
    await ask_question(callback.message, state, "quiz_more")


@router.callback_query(F.data == "quiz_change_topic")
async def quiz_change_topic(callback: CallbackQuery, state: FSMContext):
    await quiz_start(callback.message, state)