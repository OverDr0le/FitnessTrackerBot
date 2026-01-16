import aiohttp
from configs.config_reader import config


WEATHER_API = config.weather_api.get_secret_value()

async def get_city_temp(city_name:str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['main']['temp']
            
    print(f"Ошибка: {response.status}")
    return None