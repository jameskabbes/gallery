from gallery.client import Client
import asyncio
import datetime as datetime_module

from gallery.services.user_access_token import UserAccessToken
from gallery.services.user import User
from gallery.schemas import user_access_token as user_access_token_schema, user as user_schema

from gallery.services import auth_credential
from gallery import utils


async def main():
    c = Client()

    async with c.AsyncSession() as session:

        a = await UserAccessToken.create(
            {
                'admin': True,
                'c': c,
                'session': session,
                'create_model': user_access_token_schema.UserAccessTokenAdminCreate(
                    expiry=datetime_module.datetime.now() + datetime_module.timedelta(minutes=5),
                    user_id='1'
                )
            }
        )

        print(a.expiry)
        print(a.issued)

        payload = dict(UserAccessToken.to_payload(a))
        print(payload)
        print(payload['exp'].timestamp())
        d = c.jwt_encode(payload)
        print(d)

        print(c.jwt_decode(d))


if __name__ == '__main__':
    asyncio.run(main())
