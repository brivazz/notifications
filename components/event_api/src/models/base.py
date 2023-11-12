"""Базовая модель."""

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    class Config:
        model_load = orjson.loads
        model_dump = orjson_dumps
