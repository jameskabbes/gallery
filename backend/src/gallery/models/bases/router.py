from abc import ABC
from typing import TypeVar, Type, List, Callable, ClassVar
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Session, select
from functools import wraps
from enum import Enum


class Router:

    _PREFIX: ClassVar[str] = ""
    _TAGS: ClassVar[list[str | Enum] | None] = None

    def __init__(self):
        self.router = APIRouter(prefix=self._PREFIX, tags=self._TAGS)

    # def get_item(self, func: Callable) -> Callable:
    #     @wraps(func)
    #     async def wrapper(*args, db: Session = Depends(get_session), **kwargs):
    #         # Extract the ID value from kwargs based on what the endpoint defined
    #         # Get the first parameter value
    #         id_value = next(iter(kwargs.values()))
    #         id_field = func.__annotations__.get(
    #             next(iter(kwargs)), int).__name__

    #         query = select(self.model).where(
    #             getattr(self.model, id_field) == id_value)
    #         item = db.exec(query).first()
    #         if item is None:
    #             raise HTTPException(
    #                 status_code=404, detail=f"{self.model.__name__} not found")
    #         return item
    #     return wrapper

    # def setup_routes(self):
    #     # Other routes remain similar but could also use decorators if needed
    #     model_class = self.model

    #     @self.router.post("/", response_model=model_class, status_code=status.HTTP_201_CREATED)
    #     async def create_item(item: model_class, db: Session = Depends(get_session)):
    #         db_item = model_class(**item.dict())
    #         db.add(db_item)
    #         db.commit()
    #         db.refresh(db_item)
    #         return db_item

    #     # ... other routes ...
