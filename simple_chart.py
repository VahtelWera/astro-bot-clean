import math
from datetime import datetime, timezone, timedelta

# Простая формула для примерного положения Солнца
def get_sun_sign(month, day):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Овен"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Телец"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Близнецы"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Рак"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Лев"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Дева"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Весы"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Скорпион"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Стрелец"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Козерог"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Водолей"
    else:
        return "Рыбы"

# Простая формула для Луны (приближённо)
def get_moon_phase(year, month, day):
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    lday = (day + math.floor((month + 1) * 2.6) + k + math.floor(k / 4) + math.floor(j / 4) + 5 * j) % 30
    return lday

def get_moon_sign(year, month, day):
    lday = get_moon_phase(year, month, day)
    if lday < 2.5: return "Овен"
    if lday < 5.0: return "Телец"
    if lday < 7.5: return "Близнецы"
    if lday < 10.0: return "Рак"
    if lday < 12.5: return "Лев"
    if lday < 15.0: return "Дева"
    if lday < 17.5: return "Весы"
    if lday < 20.0: return "Скорпион"
    if lday < 22.5: return "Стрелец"
    if lday < 25.0: return "Козерог"
    if lday < 27.5: return "Водолей"
    return "Рыбы"

def calculate_natal_chart(year, month, day, hour, minute, lat, lng):
    sun_sign = get_sun_sign(month, day)
    moon_sign = get_moon_sign(year, month, day)
    
    # Примерное время восхода для определения ASC
    asc_sign = sun_sign
    
    return {
        "Солнце": sun_sign,
        "Луна": moon_sign,
        "Асцендент": asc_sign,
        "Дата": f"{day}.{month}.{year} {hour}:{minute}",
        "Примечание": "⚠️ Это приблизительный расчёт. Для точного нужны эфемериды."
    }

if __name__ == "__main__":
    print("🔮 Астрологический расчёт (приближённый)")
    year = int(input("Год рождения: "))
    month = int(input("Месяц (1-12): "))
    day = int(input("День: "))
    hour = int(input("Час (0-23): "))
    minute = int(input("Минуты: "))
    
    chart = calculate_natal_chart(year, month, day, hour, minute, 0, 0)
    print("\n📊 Результат:")
    for key, value in chart.items():
        print(f"{key}: {value}")
    
    input("\nНажми Enter для выхода...")