from fastapi import FastAPI
import pydantic
from src import types

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
