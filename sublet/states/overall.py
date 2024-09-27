from telebot.handler_backends import State, StatesGroup

class OverallState(StatesGroup):
    """ Класс со всеми необходимыми состояниями """

    add_post = State()
    move_in = State()
    checkout = State()
    address = State()
    city = State()
    type = State()
    description = State()
    photos = State()
    more_photos = State()
    test = State()

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
