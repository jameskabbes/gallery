from gallery import client, models  # type: ignore
import asyncio
from sqlmodel import SQLModel


async def main():
    c = client.Client()

    async with c.db_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == '__main__':
    asyncio.run(main())
