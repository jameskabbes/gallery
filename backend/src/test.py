from gallery.client import Client
import asyncio
import datetime as datetime_module

from gallery import models  # type: ignore

from gallery.models import sign_up

a = models.User(
    id='1', email='a@a.com', user_role_id=1, phone_number=None, username=None, hashed_password=None)

b = sign_up.SignUp(issued=datetime_module.datetime.now(), expiry=datetime_module.datetime.now(
) + datetime_module.timedelta(days=1), email='a@a.com')

c = b.encode()


async def main():
    c = Client()

    async with c.AsyncSession() as session:
        print(session)

if __name__ == '__main__':
    asyncio.run(main())
