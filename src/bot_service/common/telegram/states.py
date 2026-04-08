from aiogram.fsm.state import State, StatesGroup


class AddVacancyState(StatesGroup):
    waiting_for_text = State()
