from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from gallery import config, types, utils
from gallery.objects import studios, studio

import os

app = FastAPI()

# Initialize PyMongo client
mongo_client = utils.get_pymongo_client()
databases = {database: mongo_client.get_database(
    database) for database in mongo_client.list_database_names()}


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/studios/")
async def get_studios() -> studios.Studios.PluralByIdType:
    return studios.Studios.find(databases[studios.Studios.COLLECTION_NAME])
