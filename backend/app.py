from fastapi import FastAPI
import pydantic
from src import types
import threading

app = FastAPI()


@app.get('/')
def home() -> str:
    return "Gallery Backend"


@app.get("/image/{image_id}/file")
def get_image_file(image_id: types.ImageVersion.model_fields['id'].annotation):
    pass


@app.get("/image/{image_id}")
def get_image(image_id: types.ImageVersion.model_fields['id'].annotation) -> str:
    pass


if __name__ == "__main__":
    # Start MongoDB in a separate thread
    mongodb_thread = threading.Thread(target=run_mongodb)
    mongodb_thread.start()

    # Start FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
