from fastapi import FastAPI
from pymongo import MongoClient
from src import config

app = FastAPI()

# Initialize PyMongo client
mongo_client = MongoClient(port=config.MONGODB_PORT)
mongodb = mongo_client[config.MONGODB_DB]


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/users")
async def get_users():
    # Assuming you have a collection named 'users'
    users = list(mongodb['test'].find())
    return {"users": users}

if __name__ == "__main__":
    # Start FastAPI server using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.UVICORN_PORT)
