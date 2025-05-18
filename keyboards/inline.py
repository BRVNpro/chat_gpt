from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def fact_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Хочу ещё факт", callback_data="random")],
        [InlineKeyboardButton(text="🔙 Закончить", callback_data="start")]
    ])
