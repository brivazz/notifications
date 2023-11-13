"""Модуль генерации рандомных временных зон."""

# import random

# import pytz


class User:
    """Генерирует рандомные временные зоны пользователей."""

    async def get_timezones(self, quantity: list) -> list:
        """Метод получения временной зоны пользователей."""
        # timezones = pytz.all_timezones
        result = []
        for item in quantity:
            timezone_dict = {
                'user_id': item,
                # 'timezone': random.choice(timezones)
                'timezone': 'Europe/Moscow',
            }
            result.append(timezone_dict)
        return result
