from aiogram.types import KeyboardButton,ReplyKeyboardMarkup

def male_female_kb():
    kb = [
        [KeyboardButton(text = "Мужчина")],
        [KeyboardButton(text = "Женщина")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите свой пол...")