import asyncio
from src.gallery import utils


async def main():
    print(utils.hash_password('password'))


if __name__ == '__main__':
    asyncio.run(main())
