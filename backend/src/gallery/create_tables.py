import asyncio
from sqlmodel import SQLModel
from src.gallery import models
from backend.src.gallery import config


async def main():
    async with config.DB_ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == '__main__':
    asyncio.run(main())
