from aiogram.fsm.state import State, StatesGroup


class OverallState(StatesGroup):
    """Класс со всеми необходимыми состояниями"""

    add_post = State()
    check_in = State()
    check_out = State()
    address = State()
    city = State()
    type = State()
    description = State()
    photos = State()
    more_photos = State()
    test1 = State()
    test2 = State()

    edit = State()
    edit_address = State()
    edit_description = State()
    change_type = State()
    change_status = State()
    change_description = State()
    change_dates = State()
    change_photos = State()

    free_city = State()
    free_dates = State()
    free_show = State()
    variants_show = State()

    notifications = State()
