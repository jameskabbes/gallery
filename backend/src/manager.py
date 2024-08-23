import asyncio
from gallery import get_client, models, utils
from sqlmodel import Field, Session, SQLModel, select
import main
import time
import datetime

c = get_client()


async def go():
    with Session(c.db_engine) as session:
        user = models.User.get_by_key_value(session, 'username', 'admin')
        print(user)

        user_private = models.UserPrivate.model_validate(user)
        print(user_private)


if __name__ == '__main__':
    asyncio.run(go())
