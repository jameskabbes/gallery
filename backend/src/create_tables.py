from backend.src.gallery.models import tables
from gallery import client
import asyncio
from sqlmodel import SQLModel


async def main():
    c = client.Client()

    async with c.db_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == '__main__':
    asyncio.run(main())
