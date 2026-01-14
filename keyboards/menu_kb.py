from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_kb():
    kb = [
        [InlineKeyboardButton(text = "Изменить профиль", callback_data= 'set_profile')],
        [InlineKeyboardButton(text = "Внести приём пищи", callback_data= 'add_food'),InlineKeyboardButton(text = "Внести выпитую воду",callback_data="add_water")],
        [InlineKeyboardButton(text = "Внести активность", callback_data="add_activity")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

