from abc import ABC
from typing import TypeVar, Type, List, Callable, ClassVar, TYPE_CHECKING, Generic, Protocol, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.routing import APIRoute
from sqlmodel import SQLModel, Session, select
from functools import wraps, lru_cache
from enum import Enum
from .. import client, models, types, services
from ..services import base as base_service
from ..schemas import pagination as pagination_schema
from ..auth import utils as auth_utils


def get_pagination(max_limit: int = 100, default_limit: int = 10):
    def dependency(limit: int = Query(default_limit, ge=1, le=max_limit, description='Quantity of results'), offset: int = Query(0, ge=0, description='Index of the first result')):
        return pagination_schema.Pagination(limit=limit, offset=offset)
    return dependency


class HasService(Generic[services.TServiceProtocol], Protocol):
    _SERVICE: Type[services.TServiceProtocol]


class Router(
    Generic[
        models.TModel,
        types.TId,
        base_service.TCreateModel,
        base_service.TUpdateModel,
        base_service.TAfterCreateCustomParams_contra,
        base_service.TAfterReadCustomParams_contra,
        base_service.TAfterUpdateCustomParams_contra,
        base_service.TAfterDeleteCustomParams_contra,
    ],
    HasService[base_service.ServiceProtocol[
        models.TModel,
        types.TId,
    ]],
):

    _ADMIN: ClassVar[bool]
    _PREFIX: ClassVar[str]
    _TAGS: ClassVar[list[str | Enum] | None]

    def __init__(self, client: client.Client):

        prefix = self._PREFIX
        if self._ADMIN:
            prefix = f'/admin{prefix}'

        tags = self._TAGS
        if self._ADMIN:
            tags = ['Admin'] + (tags or [])

        self.router = APIRouter(prefix=prefix, tags=tags)
        self.client = client
        self._set_routes()

    def _set_routes(self) -> None:
        pass

    @classmethod
    async def get(cls, c: client.Client, authorization: auth_utils.GetAuthReturn, id: types.TId) -> models.TModel:

        async with c.AsyncSession() as session:
            try:
                item = await cls._SERVICE.read({
                    'admin': cls._ADMIN,
                    'c': c,
                    'session': session,
                    'id': id,
                    'authorized_user_id': authorization._user_id,
                })
            except base_service.NotFoundError as e:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail=e.error_message)
            except Exception as e:
                raise

            return item

    @classmethod
    @lru_cache(maxsize=None)
    def not_found_message(cls) -> str:
        return f'{cls.__name__} not found'

    @classmethod
    @lru_cache(maxsize=None)
    def already_exists_message(cls) -> str:
        return f'{cls.__name__} already exists'

    @classmethod
    @lru_cache(maxsize=None)
    def not_found_exception(cls) -> HTTPException:
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=cls.not_found_message())

    @classmethod
    @lru_cache(maxsize=None)
    def already_exists_exception(cls) -> HTTPException:
        return HTTPException(status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    @classmethod
    @lru_cache(maxsize=None)
    def get_responses(cls):
        return {}

    @classmethod
    @lru_cache(maxsize=None)
    def post_responses(cls):
        return {}

    @classmethod
    @lru_cache(maxsize=None)
    def patch_responses(cls):
        return {}

    @classmethod
    @lru_cache(maxsize=None)
    def delete_responses(cls):
        return {}

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
