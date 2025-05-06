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

    print(utils.hash_password('password'))


if __name__ == '__main__':
    asyncio.run(main())
