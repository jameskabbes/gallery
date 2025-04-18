from gallery.client import Client
import asyncio
import datetime as datetime_module

from gallery import models as models
from gallery.models import sign_up, user


async def main():
    c = Client()

    async with c.AsyncSession() as session:
        print(session)

        # await user.User.authenticate(session, 'username', 'password')
        await user.User.read({
            'session': session,
            'id': '123',
            'c': c,
        })


if __name__ == '__main__':
    asyncio.run(main())
