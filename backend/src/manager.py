import asyncio
import typing
from fastapi import Depends
from sqlmodel import Session
from gallery import models
# Adjust the import as necessary
from main import c

from sqlmodel import select

from google.oauth2 import id_token
from google.auth.transport import requests


async def create_tables():
    c.create_tables()


async def main():
    with Session(c.db_engine) as session:
        pass

        # #
        # read_scope = models.Scope(id='users.read')
        # write_scope = models.Scope(id='users.write')
        # session.add(read_scope)
        # session.add(write_scope)
        # session.commit()

        # user = models.UserCreate(
        #     email='a@a.com'
        # ).create()
        # session.add(user)
        # session.commit()

        # #
        # user_scope_read = models.UserScope(
        #     user_id=user.id, scope_id=read_scope.id)
        # user_scope_write = models.UserScope(
        #     user_id=user.id, scope_id=write_scope.id)
        # session.add(user_scope_read)
        # session.add(user_scope_write)
        # session.commit()

        # #
        # api_key = models.APIKeyCreate(user_id=user.id).create()
        # session.add(api_key)
        # session.commit()

        # #
        # api_key_scope_read = models.APIKeyScope(
        #     api_key_id=api_key.id, scope_id=read_scope.id)
        # api_key_scope_write = models.APIKeyScope(
        #     api_key_id=api_key.id, scope_id=write_scope.id)
        # session.add(api_key_scope_read)
        # session.add(api_key_scope_write)
        # session.commit()

        # user = session.exec(select(models.User)).first()

        # print(user)
        # for user_scope in user.scopes:
        #     print(user_scope)

        # for use_api_key in user.api_keys:
        #     print(use_api_key)


if __name__ == "__main__":
    # Run the example
    asyncio.run(
        # main()
        create_tables()
    )
