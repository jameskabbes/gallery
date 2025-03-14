from gallery import models, client
import asyncio


async def main():
    c = client.Client()
    async with c.AsyncSession() as session:
        async with c.db_async_engine.begin() as conn:
            await conn.run_sync(models.BaseDB.metadata.create_all)
        await session.commit()

if __name__ == '__main__':
    asyncio.run(main())
