# """Модуль с функцией-провайдером для подключения к Rabbit."""

# import aiormq

# connection: aiormq.Connection | None = None
# channel: aiormq.Channel | None = None


# async def get_rabbit() ->  aiormq.abc.AbstractConnection:
#     """Dependency injection для подключения к Rabbit."""
#     return channel