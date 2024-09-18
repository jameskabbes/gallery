import asyncio
import typing
from fastapi import Depends
from sqlmodel import Session
from gallery import models
# Adjust the import as necessary
from main import login, c, post_user

from google.oauth2 import id_token
from google.auth.transport import requests


async def main():

    a = models.UserCreate(
        email="a@a.com")
    print(a)

    b = a.create()
    print(b)

    with Session(c.db_engine) as session:
        pass


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
