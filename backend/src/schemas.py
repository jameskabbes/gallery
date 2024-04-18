import pydantic
from src import types


class Person(pydantic.BaseModel):
    id: int
    name: str


class Image:

    class Version(pydantic.BaseModel):
        id: types.Nanoid

    class Group:
        pass
