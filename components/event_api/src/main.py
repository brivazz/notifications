"""API управления уведомлениями."""

import contextlib

import fastapi
import uvicorn
from api.v1 import events
from broker.rabbit import rabbit_storage
from core.config import settings
from db.mongo import mongo_storage


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> None:
    """Выполняет необходимые действия при запуске/остановке приложения."""
    await mongo_storage.on_startup(settings.mongo_uri)
    await rabbit_storage.on_startup(settings.rabbit_uri)
    yield
    await mongo_storage.on_shutdown()
    await rabbit_storage.on_shutdown()


def init_app() -> fastapi.FastAPI:
    """Инициализирует экземпляр FastAPI."""
    return fastapi.FastAPI(
        title=settings.project_name,
        docs_url='/api/openapi',
        openapi_url='/api/openapi.json',
        default_response_class=fastapi.responses.ORJSONResponse,
        debug=settings.debug,
        lifespan=lifespan,
    )


app = init_app()

app.include_router(events.events_router, prefix='/api/v1/notifications', tags=['notifications'])


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8002, reload=True)
