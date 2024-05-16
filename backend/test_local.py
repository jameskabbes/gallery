import asyncio
import re
from gallery import config, types, utils
from gallery.objects import media, studio, event, media_types

from app import c

c.sync_with_local()

# im = image_file.File.get_by_id(c.db['files'], 'Hr0aOpWOF5b3')
# print(im)

# print(im.build_path(config.DATA_DIR))

"""

async def main():
    response = await app.delete_studio('p42pGYcU69z4')
    print(response)

# Python 3.7+
asyncio.run(main())

"""
