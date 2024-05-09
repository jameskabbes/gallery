# import asyncio
# import re
# from gallery import config, types, utils
# from gallery.objects import studios, events, medias
from gallery.objects import client

c = client.Client(config={'uvicorn': {'port': 8088},
                  'mongodb': {'port': 27018}})

"""

async def main():
    response = await app.delete_studio('p42pGYcU69z4')
    print(response)

# Python 3.7+
asyncio.run(main())

"""
