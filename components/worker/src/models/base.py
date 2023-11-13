"""Файл базовой модели."""

import orjson
from pydantic import BaseModel


def orjson_dumps(value, *, default):
    """Сериализует объект 'value' в JSON с использованием библиотеки orjson.

    Args:
        value: Основной объект, который нужно сериализовать в JSON.
        default: Функция-обратный вызов (callback), которая будет использоваться для сериализации
                значений, которые не поддерживаются нативно в JSON.

    Returns:
        Строка, представляющая основной объект 'v' в формате JSON.

    """
    return orjson.dumps(value, default=default).decode()


class BaseOrjsonModel(BaseModel):
    """Базовая модель."""

    class Config:
        model_load = orjson.loads
        model_dump = orjson_dumps
