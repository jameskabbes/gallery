import asyncio
from gallery import get_client, models
from sqlmodel import Field, Session, SQLModel

c = get_client()


async def main():

    # session = Session(c.db_engine)

    c.create_tables()

    # st = studio.Studio(id=1, name='test', test=2)
    # st.add_to_db(Session(c.db_engine))

    # print(models.Studio.id_exists(session, 1))


if __name__ == '__main__':
    asyncio.run(main())
