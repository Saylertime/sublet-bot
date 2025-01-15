from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_markup(buttons):
    """Создает кнопки для ответа"""
    inline_keyboard = []
    for text, callback_data in buttons:
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        inline_keyboard.append([button])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_markup_3_buttons(buttons):
    """Создает кнопки для ответа в две колонки"""
    inline_keyboard = []

    # Проходимся по кнопкам с шагом 2, чтобы группировать их по парам
    for i in range(0, len(buttons), 3):
        row = []
        for text, callback_data in buttons[i:i+3]:
            button = InlineKeyboardButton(text=text, callback_data=callback_data)
            row.append(button)
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_markup_with_url(buttons):
    inline_keyboard = []
    for text, url, callback_data in buttons:
        if url:
            button = InlineKeyboardButton(text=text, url=url)
        elif callback_data:
            button = InlineKeyboardButton(text=text, callback_data=callback_data)
        else:
            continue
        inline_keyboard.append([button])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_markup_with_url_2_rows(buttons):
    inline_keyboard = []
    row = []  # Временный список для формирования строки

    for index, (text, url, callback_data) in enumerate(buttons):
        if url:
            button = InlineKeyboardButton(text=text, url=url)
        elif callback_data:
            button = InlineKeyboardButton(text=text, callback_data=callback_data)
        else:
            continue

        row.append(button)  # Добавляем кнопку в текущую строку

        # Если в строке две кнопки или это последняя кнопка, добавляем строку в клавиатуру
        if len(row) == 2 or index == len(buttons) - 1:
            inline_keyboard.append(row)
            row = []  # Очищаем строку для следующей итерации

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
