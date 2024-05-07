from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from gallery import config, types, utils
from gallery.objects import studios, studio, events, event

import os

app = FastAPI()

# Initialize PyMongo client
mongo_client = utils.get_pymongo_client()
db = mongo_client['gallery']


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/studios/")
async def get_studios() -> studios.Studios.PluralByIdType:
    return studios.Studios.find(db[studios.Studios.COLLECTION_NAME])


@app.get("/events/")
async def get_events() -> events.Events.PluralByIdType:
    return events.Events.find(db[events.Events.COLLECTION_NAME])
