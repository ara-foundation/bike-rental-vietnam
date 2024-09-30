from math import inf
from django.db.models import Sum
from bike_rental.models import Bike, Season, Price
from django.utils import timezone
from datetime import datetime
from decimal import Decimal


def get_total_bikes_for_brand(brand_name):
    total_bikes = Bike.objects.filter(bike_model__brand__name=brand_name).aggregate(
        total=Sum("amount")
    )["total"]
    return total_bikes or 0  # Return 0 if no bikes are found

def calculate_total_price(duration, amount_bikes, prices):
    total_price = float(inf)  # Инициализируем с бесконечностью
    calculated_price = 0

    # Логируем начальные значения
    print(f"Начальные значения: Duration: {duration}, Amount of Bikes: {amount_bikes}, Prices: {prices}")

    # Рассчитываем цену для duration <= duration
    for price in prices:
        if price.duration <= duration:
            calculated_price = (Decimal(price.cost) / Decimal(price.duration)) * int(duration) * int(amount_bikes)
            print(f"Цена для {price.duration} дней: {calculated_price}")

    # Логируем рассчитанную цену
    print(f"Рассчитанная цена для duration <= duration: {calculated_price}")

    # Рассчитываем цену для duration > duration
    for price in prices:
        if price.duration > duration:
            total_price = min((Decimal(price.cost) * int(amount_bikes)), calculated_price)
            print(f"Обновленная цена для {price.duration} дней: {total_price}")

    # Логируем итоговую цену
    if total_price == float(inf):
        print("Ошибка: Не удалось рассчитать общую цену.")
    else:
        print(f"Итоговая цена: {total_price}")

    return total_price