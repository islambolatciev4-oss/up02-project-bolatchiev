"""Логика каталога без интерфейса: индикатор «много/мало» и цвет подсветки.

Вынесена отдельно, чтобы тесты работали без tkinter. В catalog.py эти функции
подключаются под теми же именами (_indicator, _get_card_color).
"""
from config import LOW_STOCK_LIMIT, MANY_LIMIT
from styles_colors import COLOR_HIGHLIGHT, COLOR_MAIN_BG


def _get_card_color(qty):
    """
    Возвращает цвет фона карточки.

    :param qty: количество товара
    :return: HEX-цвет (#ff8080 при количестве <= 3, иначе белый)
    """
    return COLOR_HIGHLIGHT if qty <= LOW_STOCK_LIMIT else COLOR_MAIN_BG


def _indicator(qty):
    """
    Индикатор «много/мало» (порог 5).

    :param qty: количество товара
    :return: «много» или «мало»
    """
    return "много" if qty > MANY_LIMIT else "мало"
