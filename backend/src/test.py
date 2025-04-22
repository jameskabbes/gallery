from gallery.client import Client
import asyncio
import datetime as datetime_module

from gallery.services.user_access_token import UserAccessToken
from gallery.services.user import User
from gallery.schemas import user_access_token as user_access_token_schema, user as user_schema

from gallery import utils


async def main():
    c = Client()

    async with c.AsyncSession() as session:

        # print(utils.hash_password('password'))

        user = await User.read(
            {
                'admin': True,
                'c': c,
                'session': session,
                'id': '1'
            }
        )

        user_private = user_schema.UserPrivate.model_validate(user)
        print(user_private)


if __name__ == '__main__':
    asyncio.run(main())
