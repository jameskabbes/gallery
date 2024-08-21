import asyncio
from gallery import get_client, models, utils
from sqlmodel import Field, Session, SQLModel
import main
import time
import datetime

c = get_client()


async def go():
    a = await main.get_current_user(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3YWFhYWE4YS0wMWQ5LTQ4OWEtOGFmZC01NTU5MDA2ZjNkYzQiLCJpYXQiOjE3MjQyNTUxNzguNzg4ODk3fQ.hN1cjM3zWiGWinmIKYDmJC319KMqkBCmOPASB5oyad0"
    )

    print(a)


if __name__ == '__main__':
    asyncio.run(go())
