"""API управления уведомлениями."""

# from logging import config as logging_config

# import backoff
import uvicorn
from aio_pika import connect_robust
# from aio_pika.exceptions import AMQPException
# from motor.motor_asyncio import AsyncIOMotorClient
import fastapi
# from fastapi.responses import ORJSONResponse

from api.v1 import events#, templates, schedulers
# from db import rabbit#mongo

from core.config import settings
from db.mongo import mongo_storage
# from core.logger import LOGGING
from faststream.rabbit import RabbitBroker
from faststream.rabbit.fastapi import RabbitRouter
from faststream import Context, FastStream
from contextlib import asynccontextmanager
from broker.rabbit import rabbit_storage
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    await mongo_storage.on_startup([f'{settings.mongo_host}:{settings.mongo_port}'])
    await rabbit_storage.on_startup(settings.rabbit_uri)
    yield
    await mongo_storage.on_shutdown()
    await rabbit_storage.on_shutdown()

def init_app() ->fastapi.FastAPI:
    """Инициализирует экземпляр FastAPI."""
    return fastapi.FastAPI(
        title=settings.project_name,
        docs_url='/api/openapi',
        openapi_url='/api/openapi.json',
        default_response_class=fastapi.responses.ORJSONResponse,
        debug=settings.debug,
        lifespan=lifespan
    )

app = init_app()


app.include_router(events.events_router, prefix='/api/v1/notifications', tags=['notifications'])
# app.include_router(templates.router, prefix='/api/v1/templates', tags=['templates'])
# app.include_router(schedulers.router, prefix='/api/v1/schedulers', tags=['schedulers'])

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8002, reload=True)
