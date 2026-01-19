from aiogram.types import KeyboardButton,ReplyKeyboardMarkup

def activity_kb():
    kb = [
        [KeyboardButton(text = "Прогулка"), KeyboardButton(text = "Бег (средний темп)")],
        [KeyboardButton(text = "Плавание"), KeyboardButton(text = "Силовая тренировка")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите активность...")