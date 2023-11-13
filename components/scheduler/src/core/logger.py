"""Модуль с настройкой логгирования."""

import json
import sys
import typing

from loguru import logger


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
    ],
}

logger.configure(**loguru_config)
