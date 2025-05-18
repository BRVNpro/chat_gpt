from aiogram.fsm.state import State, StatesGroup

class TalkStates(StatesGroup):
    selecting_character = State()
    chatting = State()
