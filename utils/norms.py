from utils.city_temp import get_city_temp

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
            return int(10*weight+6.25*height-5*age+5)
        else:
            return int(10*weight+6.25*height-5*age - 161)
    except Exception as e:
        print(f"Ошибка расчёта нормы калорий {e}")
        return None

async def water_norm(weight:int, height:int, city:str | None):
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
    if city:
        temperature = await get_city_temp(city)
        if temperature > 25:
            return weight*30 + 500
    else:
        return weight*30


            





    
