from fastapi import FastAPI
from gallery import client
from gallery.models import user
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
c = client.Client(config={})

app.include_router(user.Router(c).router)