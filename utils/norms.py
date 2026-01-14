import aiohttp
from configs.config_reader import config

WEATHER_API = config.weather_api.get_secret_value()

def calories_norm(weight:int, height:int, age:int, sex:str):
    '''
    Расчёт формулы калорий по формуле Миффлина-Сен Жеора

    Для мужчин: ПБМ = (10 × вес в кг) + (6,25 × рост в см) - (5 × возраст в годах) + 5
    Для женщин: ПБМ = (10 × вес в кг) + (6,25 × рост в см) - (5 × возраст в годах) − 161
    
    :param weight: вес в кг
    :type weight: int
    :param height: рост в см
    :type height: int
    :param age: возраст в полных годах
    :type age: int
    :param sex: пол
    :type sex: str
    '''
    try:
        if age == 'Мужчина':
            return 10*weight+6.25*height-5*age+5
        else:
            return 10*weight+6.25*height-5*age - 161
    except Exception as e:
        print(f"Ошибка расчёта нормы калорий {e}")
        return None

async def water_norm(weight:int, height:int, city:str):
    '''
    Расчёт нормы расхода воды без учёта активностей

    water_norm = weight*30 + 500 (при температуре >25 C)
    
    :param weight: вес в кг
    :type weight: int
    :param height: рост в см
    :type height: int
    :param city: название населённого пункта
    :type city: str

    return value: int, количесиво мл воды
    '''

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temperature = data['main']['temp']
                if temperature > 25:
                    return weight*30 + 500
                else:
                    return weight*30
            else:
                print("Ошбика в запросе температуры")
                return weight*30


            





    
