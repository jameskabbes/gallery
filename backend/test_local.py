import asyncio
import re
from gallery import config, types, utils
from gallery.objects import media, studio, event, media_types

from app import c
import app


id = 'nqWxD2VvRLXP'


async def main():
    response = await app.get_studios()
    print(response)

if __name__ == '__main__':
    asyncio.run(main())
