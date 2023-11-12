# import orjson

# # import os, sys
# # current = os.path.dirname(os.path.realpath(__file__))
# # parent = os.path.dirname(os.path.dirname(os.path.dirname(current)))
# # sys.path.append(parent)
# # sys.path.append(current)
# # print(current)
# # print(parent)
# from faststream.rabbit import RabbitBroker
# from faststream import FastStream
# # from .rabbitmq import broker
# # broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
# # app = FastStream(broker)
# import functools
# import dataclasses
# from functools import lru_cache
# import logging
# from fastapi import Depends
# from db.rabbit import get_broker


# class BaseEventService:
#     # broker = RabbitBroker("amqp://guest:guest@localhost:5672/", log_level=logging.DEBUG)
#     def __init__(self, broker: RabbitBroker):
#     # def __init__(self):
#         self.broker = broker

#     async def send_event(self, event: dict | list[dict]):
#         event = orjson.dumps(event.model_dump())
#         # await send_to_rabbitmq(self.rabbitmq_queue, event)
#         await self.broker.start()
#         await self.broker.publish(
#             message=event,
#             # queue='notification',
#             routing_key='notification.send'
#         )
#         await self.broker.close()

#     # @staticmethod
#     # def subscribe(self, queue):
#         # def decorator(func):
#         #     @functools.wraps(func)
#         #     # @broker.subscriber(queue)
#         #     async def wrapper(*args, **kwargs):
#         #         return await func(kwargs)
#         #     self.broker.subscriber(queue)(wrapper)
#         # return decorator
#     async def subscribe(self):
#         @self.broker.subscriber('notification.send')
#         def on_message(msg):
#             return msg
#         return on_message()


# # base_event_service: BaseEventService | None = None

# @lru_cache
# def get_base_event_service(
#     broker: RabbitBroker = Depends(get_broker)
# ) -> BaseEventService | None:
#     """Возвращает объект BaseEventService или None."""
#     return BaseEventService(broker)
