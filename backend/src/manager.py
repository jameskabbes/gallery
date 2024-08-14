import asyncio
from gallery import get_client, models, utils
from sqlmodel import Field, Session, SQLModel

c = get_client()


async def main():

    c.create_tables()
    # print(utils.hash_password('password'))
    # print(utils.verify_password('password', utils.hash_password('password')))

if __name__ == '__main__':
    asyncio.run(main())
