"""Модуль работы с ресурсами: заглушка, логотип, иконка, фото товаров."""
import os

from config import BASE_DIR

PATH_RESOURCES = os.path.join(BASE_DIR, "resources")
PATH_IMAGES = os.path.join(PATH_RESOURCES, "images")
PATH_PICTURE = os.path.join(PATH_RESOURCES, "picture.png")   # заглушка
PATH_LOGO = os.path.join(PATH_RESOURCES, "logo.png")         # логотип
PATH_ICON = os.path.join(PATH_RESOURCES, "icon.ico")         # иконка приложения


def product_image_path(image_name):
    """
    Возвращает путь к фото товара или None, если файла нет.

    :param image_name: имя файла из БД (например, pizza.png) или пустое значение
    :return: путь к существующему файлу либо None
    """
    if not image_name:
        return None
    for folder in (PATH_IMAGES, PATH_RESOURCES):
        path = os.path.join(folder, str(image_name))
        if os.path.isfile(path):
            return path
    return None


def load_image(path, size=(100, 100)):
    """
    Загружает изображение с точным размером.

    :param path: путь к файлу
    :param size: (ширина, высота)
    :return: ImageTk.PhotoImage или None
    """
    try:
        from PIL import Image, ImageTk
        if not path or not os.path.isfile(path):
            return None
        return ImageTk.PhotoImage(Image.open(path).resize(size))
    except Exception as error:
        print(f"Ошибка загрузки {path}: {error}")
        return None


def load_image_proportional(path, max_size=(100, 100)):
    """
    Загружает изображение с сохранением пропорций (для логотипа).

    :param path: путь к файлу
    :param max_size: максимальные (ширина, высота)
    :return: ImageTk.PhotoImage или None
    """
    try:
        from PIL import Image, ImageTk
        if not path or not os.path.isfile(path):
            return None
        img = Image.open(path)
        img.thumbnail(max_size)   # thumbnail сохраняет пропорции
        return ImageTk.PhotoImage(img)
    except Exception as error:
        print(f"Ошибка загрузки {path}: {error}")
        return None


def get_product_image(image_name, size=(100, 100)):
    """
    Возвращает картинку товара или заглушку picture.png.

    :param image_name: имя файла изображения из БД
    :param size: (ширина, высота)
    :return: ImageTk.PhotoImage или None
    """
    path = product_image_path(image_name)
    return load_image(path or PATH_PICTURE, size)
