from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    default = State()

    check_username = State()
    recheck_username = State()

    ask_first_name = State()
    edit_first_name = State()

    ask_last_name = State()
    edit_last_name = State()

    ask_birthdate = State()
    edit_birthdate = State()

    ask_lanuage_code = State()
    edit_language_code = State()

    ask_gender = State()
    edit_gender = State()

    confirm_registration = State()
