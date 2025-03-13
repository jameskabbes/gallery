from gallery import models, client
import asyncio


async def main():
    c = client.Client()
    async with c.AsyncSession() as session:
        models.BaseDB.metadata.create_all(c.db_async_engine)
        await session.commit()

if __name__ == '__main__':
    asyncio.run(main)
