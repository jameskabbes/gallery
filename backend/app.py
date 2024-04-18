from fastapi import FastAPI
import pydantic

app = FastAPI()


@app.get("/")
def read_root() -> str:
    return "Hello world!"


class Person(pydantic.BaseModel):
    id: int
    name: str


@app.get('/person/{person_id}')
def get_person_by_id(person_id: Person.model_fields['id'].annotation) -> Person:
    return Person(id=1, name='test')
