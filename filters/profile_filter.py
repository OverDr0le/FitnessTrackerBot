from aiogram.filters import Filter
from aiogram.types import Message

from utils.city_temp import get_city_temp


class IsNumberInRange(Filter):
    def __init__(self, low_value: int, up_value:int) -> None:
        self.lower_value = low_value
        self.upper_value = up_value

    async def __call__(self, message: Message) -> bool:
        try:
            num = int(message.text)
            return self.lower_value <= num <= self.upper_value
        except (ValueError, TypeError) as e:
            print(f"Ошибка {e}")
            return False
        
class CityFilter(Filter):
    def __init__(self) -> None:
        pass
    
    async def __call__(self,message:Message):
        return bool(await get_city_temp(message.text))

        





