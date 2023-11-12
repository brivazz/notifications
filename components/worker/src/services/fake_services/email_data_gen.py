from faker import Faker
from pydantic import BaseModel, EmailStr
import uuid


class EmailData(BaseModel):
    name: str
    email: EmailStr


class EmailDataGenerator:
    # def __init__(self, user_data):
    def __init__(self):
        self.faker = Faker()

    async def generate_email_data(self, user_id: uuid.UUID) -> EmailData:
        email_data = {}
        name = self.faker.name()
        # print(name)
        email = self.faker.email()
        # print(email)
        return EmailData(name=name, email=email)

        # Здесь вы можете использовать данные пользователя для генерации персонифицированных данных для email

        # Пример: получить имя пользователя
        # if 'name' in self.user_data:
        #     name = self.user_data['name']
        #     email_data['name'] = name

        # # Пример: добавить адрес электронной почты
        # if 'email' in self.user_data:
        #     email = self.user_data['email']
        #     email_data['email'] = email

        # Продолжайте генерировать и добавлять другие персонифицированные данные, основываясь на данных пользователя

#         return email_data

# edg = EmailDataGenerator()
# edg.generate_email_data()
