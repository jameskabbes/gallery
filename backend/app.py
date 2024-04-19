from fastapi import FastAPI
import pydantic
from src import schemas

app = FastAPI()


@app.get('/')
def home() -> str:
    return "Gallery Backend"


@app.get("/image/{image_id}/file")
def get_image_file(image_id: schemas.ImageVersion.model_fields['id'].annotation):
    pass


@app.get("/image/{image_id}")
def get_image(image_id: schemas.ImageVersion.model_fields['id'].annotation) -> str:
    pass


@app.get('/person/{person_id}')
def get_person_by_id(person_id: schemas.Person.model_fields['id'].annotation) -> schemas.Person:
    return schemas.Person(id=1, name='test')
