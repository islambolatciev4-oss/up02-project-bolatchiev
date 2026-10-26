"""Модели данных для проекта УП.02."""
from datetime import datetime

from discount import calculate_price_with_discount


class Product:
    """Класс Товар (блюдо)."""

    def __init__(self, product_id, name, category, weight, price, quantity,
                 image, composition):
        """
        Инициализация товара.

        :param product_id: идентификатор
        :param name: название
        :param category: категория
        :param weight: вес порции, г
        :param price: цена
        :param quantity: количество
        :param image: имя файла с фото
        :param composition: состав
        """
        self.id = product_id
        self.name = name
        self.category = category
        self.weight = weight
        self.price = price
        self.quantity = quantity
        self.image = image
        self.composition = composition

    def total(self):
        """Общая стоимость (цена × количество)."""
        return self.price * self.quantity

    def price_with_discount(self, discount_percent):
        """Цена со скидкой."""
        return self.price * (1 - discount_percent / 100)

    def price_with_discount_auto(self, date=None):
        """Цена со скидкой по алгоритму ДЭ."""
        if date is None:
            date = datetime.now()
        return calculate_price_with_discount(self.id, self.price, date)

    def indicator(self):
        """Индикатор «много/мало» (порог 5)."""
        return "много" if self.quantity > 5 else "мало"

    def is_available(self):
        """Есть ли товар в наличии (количество > 0)."""
        return self.quantity > 0

    def info(self):
        """Строка с информацией о товаре."""
        return (
            f"{self.name} ({self.category}, {self.weight} г): "
            f"{self.price} руб. × {self.quantity} = {self.total()} руб. "
            f"({self.indicator()})"
        )


class Order:
    """Класс Заказ."""

    def __init__(self, order_id, date, client, product, quantity):
        self.id = order_id
        self.date = date
        self.client = client
        self.product = product      # объект Product
        self.quantity = quantity

    def total(self):
        """Стоимость заказа."""
        return self.product.price * self.quantity

    def info(self):
        return (
            f"Заказ №{self.id} от {self.date}: {self.client} — "
            f"{self.product.name} × {self.quantity}"
        )
