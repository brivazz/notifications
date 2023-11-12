# """Модуль с функцией-провайдером для подключения к Rabbit."""

# import aiormq

# connection: aiormq.Connection | None = None
# channel: aiormq.Channel | None = None


# async def create_connection_rabbitmq() -> aiormq.abc.AbstractConnection:
#     connection_string = ('amqp://guest:guest@127.0.0.1:5672/')
#     return await aiormq.connect(connection_string)


# async def create_channel_rabbitmq(
#     connection_: aiormq.abc.AbstractConnection,
# ) -> aiormq.abc.AbstractChannel:
#     return await connection_.channel()


# async def get_rabbit() ->  aiormq.abc.AbstractConnection:
#     """Dependency injection для подключения к Rabbit."""
#     return channel
