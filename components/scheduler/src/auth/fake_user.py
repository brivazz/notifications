import random
import pytz


class User:
    def __init__(self):
        self.timezone = self.generate_random_timezone()

    def generate_random_timezone(self):
        timezones = pytz.all_timezones
        random_index = random.randint(0, len(timezones)-1)
        return timezones[random_index]

    async def get_timezone(self):
        return self.timezone

    async def get_timezones(self, quantity: list):
        timezones = pytz.all_timezones
        # return random.sample(timezones, k=len(quantity))
        result = []
        for item in quantity:
            timezone_dict = {
                'user_id': item,
                # 'timezone': random.choice(timezones)
                'timezone': 'Europe/Moscow'
            }
            result.append(timezone_dict)
        return result
