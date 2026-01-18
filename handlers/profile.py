from typing import Any, Dict
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Bold, Text, as_marked_section, as_list

from sqlalchemy.ext.asyncio import AsyncSession

from services.user_profile import UserProfile
from filters.profile_filter import IsNumberInRange, CityFilter
from keyboards.profile_kb import male_female_kb
from utils.norms import calories_norm, water_norm

router = Router()


class SetProfile(StatesGroup):
    set_height = State()
    set_weight = State()
    set_age = State()
    set_sex = State()
    set_city = State()


# # Создаём общую точку входа в FSM для callback и Command
async def start_profile_edit(message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="Введите ваш рост в *см*:", parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(SetProfile.set_height)


# Начало FSM для заполнения профиля
# С помощью Command
@router.message(Command("set_profile"))
async def profile_edit_start(message: Message, state: FSMContext) -> None:
    await start_profile_edit(message, state)


# С помощью callback query
@router.callback_query(F.data == "set_profile")
async def profile_edit_start_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await start_profile_edit(callback.message, state)
    await callback.answer()


@router.message(SetProfile.set_height, IsNumberInRange(120, 250))
async def process_height(message: Message, state: FSMContext) -> None:
    await state.update_data(set_height=int(message.text))
    await message.answer(
        text="Теперь введите ваш вес в *кг*:", parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(SetProfile.set_weight)


@router.message(SetProfile.set_height)
async def incorrect_height(message: Message) -> None:
    await message.answer(text="Некорректно введённый рост. Попробуйте снова.")


@router.message(SetProfile.set_weight, IsNumberInRange(35, 200))
async def process_weight(message: Message, state: FSMContext) -> None:
    await state.update_data(set_weight=int(message.text))
    await message.answer(text="Сколько вам полных лет?")
    await state.set_state(SetProfile.set_age)


@router.message(SetProfile.set_weight)
async def incorrect_weight(message: Message) -> None:
    await message.answer(text="Некорректно введённый вес. Попробуйте снова.")


@router.message(SetProfile.set_age, IsNumberInRange(16, 100))
async def peocess_age(message: Message, state: FSMContext) -> None:
    await state.update_data(set_age=int(message.text))
    await message.answer(text="Выберите ваш пол:", reply_markup=male_female_kb())
    await state.set_state(SetProfile.set_sex)


@router.message(SetProfile.set_age)
async def incorrect_age(message: Message) -> None:
    await message.answer(text="Некорректно введённый возраст. Попробуйте снова.")


@router.message(SetProfile.set_sex, F.text.in_(["Мужчина", "Женщина"]))
async def process_sex(message: Message, state: FSMContext) -> None:
    await state.update_data(set_sex=message.text.lower())
    await message.answer(
        text="В каком городе вы проживаете? Эта информация поможет более точно рассчитывать норму выпитой воды в сутках.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(SetProfile.set_city)


@router.message(SetProfile.set_sex)
async def incorrect_sex(message: Message) -> None:
    await message.answer(
        text=f"Некорректно введённый пол {message.text}. Пожалуйста, выберите пол из доступных.",
        reply_markup=male_female_kb(),
    )


@router.message(SetProfile.set_city, CityFilter())
async def process_city(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(set_city=message.text)
    data: Dict[str, Any] = await state.get_data()
    norm_ccal: int | None = calories_norm(
        weight=data["set_weight"],
        height=data["set_height"],
        age=data["set_age"],
        sex=data["set_sex"],
    )
    norm_water: int | None = await water_norm(
        weight= data["set_weight"],
        height=data["set_height"],
        city = data["set_city"]
    )
    data["telegram_id"] = message.from_user.id
    data["calories_goal"] = norm_ccal
    data["water_goal"] = norm_water
    
    try:
        user = UserProfile(session=session)
        await user.save_profile(data)
        text: Text = as_list(
            Bold("Отлично! Характеристики успешно изменены."),
            as_marked_section(
                f"Рост: {data["set_height"]} см",
                f"Вес: {data["set_weight"]} кг",
                f"Пол: {data["set_sex"]}",
                f"Возраст: {data['set_age']}",
                f"Населённый пункт: {data["set_city"]}",
                marker="-",
            ),
            f"Рекомендуемая дневная норма ккал: {norm_ccal} ккал\nДневная норма воды: {norm_water} мл\nВы можете установить норму самостоятельно при помощи /change_caloriesgoal",
            sep="\n\n",
        )
        await message.answer(**text.as_kwargs())
        await state.clear()
    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
        await message.answer(
            f"Ошибка сохранения профиля"
        )
        await state.clear()


@router.message(SetProfile.set_city)
async def incorrect_city(message: Message) -> None:
    await message.answer(
        text=f"Неизвестный населённый пункт! Проверьте название и попробуйте снова."
    )


# Конец FSM


