# """Настройки логирования."""

# from core.settings import settings

# LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# LOG_DEFAULT_HANDLERS = ['console', ]

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': LOG_FORMAT
#         },
#         'default': {
#             '()': 'uvicorn.logging.DefaultFormatter',
#             'fmt': '%(levelprefix)s %(message)s',
#             'use_colors': None,
#         },
#         'access': {
#             '()': 'uvicorn.logging.AccessFormatter',
#             'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': settings.logging.level_console,
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#         'default': {
#             'formatter': 'default',
#             'class': 'logging.StreamHandler',
#             'stream': 'ext://sys.stdout',
#         },
#         'access': {
#             'formatter': 'access',
#             'class': 'logging.StreamHandler',
#             'stream': 'ext://sys.stdout',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': LOG_DEFAULT_HANDLERS,
#             'level': settings.logging.level_root,
#         },
#         'uvicorn.error': {
#             'level': settings.logging.level_uvicorn,
#         },
#         'uvicorn.access': {
#             'handlers': ['access'],
#             'level': settings.logging.level_uvicorn,
#             'propagate': False,
#         },
#     },
#     'root': {
#         'level': settings.logging.level_root,
#         'formatter': 'verbose',
#         'handlers': LOG_DEFAULT_HANDLERS,
#     },
# }

"""Модуль с настройкой логгирования."""

import json
import sys
import typing
from pathlib import Path

from notifications_sprint_1.components.event_api.src.core.config import settings
from loguru import logger

logs_dir: Path = Path(settings.base_dir).resolve().parent.parent
# log_file_path = Path.joinpath(logs_dir, '/var/log/access.log')
# err_log_file_path = Path.joinpath(logs_dir, '/var/log/errors.log')


def serialize(record: dict[str, typing.Any]) -> str:
    """Сериализует запись лога в формат JSON."""
    subset = {
        '@timestamp': str(record['time']),
        'level': record['level'].name,
        'file': record['file'].name + ':' + record['function'] + ':' + str(record['line']),
        'message': record['message'],
    }
    return json.dumps(subset)


def formatter(record: dict[str, typing.Any]) -> str:
    """Функция пользовательского форматирования логов."""
    record['extra']['serialized'] = serialize(record)
    return '{extra[serialized]}\n'


loguru_config = {
    'handlers': [
        {
            'sink': sys.stderr,
            'level': 'INFO',
            'colorize': True,
            'format': '<green>{time:YYYY-mm-dd HH:mm:ss.SSS}</green>'
            '| {thread.name} | <level>{level}</level> | '
            '<cyan>{module}</cyan>:<cyan>{function}</cyan>:'
            '<cyan>{line}</cyan> - <level>{message}</level>',
        },
        # {'sink': log_file_path, 'format': formatter, 'enqueue': True, 'rotation': '50 MB', 'encoding': 'utf-8'},
        # {
        #     'sink': err_log_file_path,
        #     'level': 'ERROR',
        #     'serialize': False,
        #     'diagnose': False,  # True - подробный отчет
        #     'backtrace': True,
        #     'retention': '7 days',
        #     'rotation': '50 MB',
        #     'encoding': 'utf-8',
        # },
    ],
}
logger.configure(**loguru_config)
