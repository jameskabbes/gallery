from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from gallery import config, types, databases

import os

app = FastAPI()

# Initialize PyMongo client
mongo_client = MongoClient(port=config.MONGODB_PORT)


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/event/{event_id}")
async def get_event(event_id: types.EventId):
    return


@app.get("/image/{image_id}")
async def get_image_file(image_id: str):
    # Replace "path_to_your_image.jpg" with the path to your image file

    path = str(config.IMAGES_DIR / '2023-11-17 Wedding' /
               str(image_id + '.JPG'))

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="image/jpeg")


if __name__ == "__main__":
    # Start FastAPI server using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.UVICORN_PORT)
