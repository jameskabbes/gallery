from ..schemas.pagination import Pagination
from .. import client, types, models, services
from pydantic import BaseModel
from typing import Protocol, Unpack, TypeVar, TypedDict, Generic, NotRequired, Literal, Self, ClassVar, Type, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel import SQLModel, select
from abc import ABC
from typing import TypeVar, Type, List, Callable, ClassVar, TYPE_CHECKING, Generic, Protocol, Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.routing import APIRoute
from sqlmodel import SQLModel, Session, select
from functools import wraps, lru_cache
from enum import Enum
from .. import client, models, types, services
from ..services import base as base_service
from ..schemas import pagination as pagination_schema, order_by as order_by_schema
from ..auth import utils as auth_utils
from collections.abc import Sequence


def get_pagination(max_limit: int = 100, default_limit: int = 10):
    def dependency(limit: int = Query(default_limit, ge=1, le=max_limit, description='Quantity of results'), offset: int = Query(0, ge=0, description='Index of the first result')):
        return pagination_schema.Pagination(limit=limit, offset=offset)
    return dependency


def order_by_depends(
    order_by: list[base_service.TOrderBy_co] = Query(
        [], description='Ordered series of fields to sort the results by, in the order they should be applied'),
    order_by_desc: list[base_service.TOrderBy_co] = Query(
        [], description='Unordered series of fields which should be sorted in a descending manner, must be a subset of "order_by" fields')
) -> list[order_by_schema.OrderBy[base_service.TOrderBy_co]]:

    order_by_set = set(order_by)
    order_by_desc_set = set(order_by_desc)

    if not order_by_desc_set.issubset(order_by_set):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='"order_by_desc" fields must be a subset of "order_by" fields')

    return [
        order_by_schema.OrderBy[base_service.TOrderBy_co](
            field=field, ascending=field not in order_by_desc_set)
        for field in order_by
    ]


class NotFoundError(HTTPException, base_service.NotFoundError):
    def __init__(self, model: Type[models.Model], id: types.Id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{model.__name__} with id {id} not found'
        )


class RouterVerbParams(TypedDict):
    c: client.Client
    authorization: auth_utils.GetAuthReturn


class WithId(Generic[types.TId], TypedDict):
    id: types.TId


class GetParams(Generic[types.TId], RouterVerbParams, WithId[types.TId]):
    pass


class GetManyParams(Generic[models.TModel, base_service.TOrderBy_co], RouterVerbParams, base_service.ReadManyBase[models.TModel, base_service.TOrderBy_co]):
    pass


class PostParams(Generic[base_service.TCreateModel], RouterVerbParams):
    create_model: base_service.TCreateModel


class PatchParams(Generic[types.TId, base_service.TUpdateModelService], RouterVerbParams, WithId[types.TId]):
    update_model: base_service.TUpdateModelService


class DeleteParams(Generic[types.TId], RouterVerbParams, WithId[types.TId]):
    pass


class HasPrefix(Protocol):
    _PREFIX: ClassVar[str]


class HasAdmin(Protocol):
    _ADMIN: ClassVar[bool]


class HasTag(Protocol):
    _TAG: ClassVar[str]


class HasService(
    Generic[models.TModel,
            types.TId,
            base_service.TCreateModel,
            base_service.TUpdateModelService,
            base_service.TOrderBy_co]):

    _SERVICE: Type[base_service.Service[
        models.TModel,
        types.TId,
        base_service.TCreateModel,
        base_service.TUpdateModelService,
        base_service.TOrderBy_co,
    ]]


class Router(Generic[
    models.TModel,
    types.TId,
    base_service.TCreateModel,
    base_service.TUpdateModelService,
    base_service.TOrderBy_co,
], HasService[
    models.TModel,
    types.TId,
    base_service.TCreateModel,
    base_service.TUpdateModelService,
    base_service.TOrderBy_co

], HasPrefix, HasAdmin, HasTag):

    def __init__(self, client: client.Client):

        prefix = self._PREFIX
        if self._ADMIN:
            prefix = f'/admin{prefix}'

        tags: list[str | Enum] = [self._TAG]
        if self._ADMIN:
            tags.append('Admin')

        self.router = APIRouter(prefix=prefix, tags=tags)
        self.client = client
        self._set_routes()

    def _set_routes(self) -> None:
        pass

    def make_get_many_endpoint(
            self,
            response_model: Type[BaseModel],
            pagination_depends: Callable = get_pagination(),
            order_by_depends: Callable = order_by_depends,
            path: str = '/',
            get_auth_kwargs: auth_utils.MakeGetAuthDependencyNoClientKwargs = {}
    ) -> Callable:

        async def endpoint(
                pagination: Annotated[pagination_schema.Pagination, Depends(pagination_depends)],
                order_bys: Annotated[list[order_by_schema.OrderBy[base_service.TOrderBy_co]], Depends(order_by_depends)],
                authorization: Annotated[auth_utils.GetAuthReturn, Depends(
                    auth_utils.make_get_auth_dependency(
                        **get_auth_kwargs, c=self.client))],
        ):

            return [response_model.model_validate(model) for model in await self.get_many({
                'authorization': authorization,
                'c': self.client,
                'pagination': pagination,
                'order_bys': order_bys,
                'query': None,
            })]

        return endpoint

    @classmethod
    async def get(cls, params: GetParams[types.TId]) -> models.TModel:

        async with params['c'].AsyncSession() as session:
            try:
                model_inst = await cls._SERVICE.read({
                    'admin': cls._ADMIN,
                    'c': params['c'],
                    'session': session,
                    'id': params['id'],
                    'authorized_user_id': params['authorization']._user_id,
                })
            except base_service.NotFoundError as e:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail=e.error_message)
            except Exception as e:
                raise

            return model_inst

    @classmethod
    async def get_many(cls, params: GetManyParams[models.TModel, base_service.TOrderBy_co]) -> Sequence[models.TModel]:
        async with params['c'].AsyncSession() as session:
            try:
                d: base_service.ReadManyParams[models.TModel, base_service.TOrderBy_co] = {
                    'admin': cls._ADMIN,
                    'c': params['c'],
                    'session': session,
                    'authorized_user_id': params['authorization']._user_id,
                    'pagination': params['pagination']}

                if 'order_bys' in params:
                    d['order_bys'] = params['order_bys']
                if 'query' in params:
                    d['query'] = params['query']

                model_insts = await cls._SERVICE.read_many(d)
            except base_service.NotFoundError as e:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail=e.error_message)
            except Exception as e:
                raise

            return model_insts

    @classmethod
    async def post(cls, params: PostParams[base_service.TCreateModel]) -> models.TModel:
        async with params['c'].AsyncSession() as session:

            try:
                model_inst = await cls._SERVICE.create({
                    'admin': cls._ADMIN,
                    'c': params['c'],
                    'session': session,
                    'authorized_user_id': params['authorization']._user_id,
                    'create_model': params['create_model'],
                })
            except base_service.AlreadyExistsError as e:
                raise
            except Exception as e:
                raise

            return model_inst

    @classmethod
    async def patch(cls, params: PatchParams[types.TId, base_service.TUpdateModelService]) -> models.TModel:
        async with params['c'].AsyncSession() as session:
            try:
                model_inst = await cls._SERVICE.update({
                    'admin': cls._ADMIN,
                    'c': params['c'],
                    'session': session,
                    'id': params['id'],
                    'authorized_user_id': params['authorization']._user_id,
                    'update_model': params['update_model'],
                })
            except base_service.NotFoundError as e:
                raise
            except Exception as e:
                raise

            return model_inst

    @classmethod
    async def delete(cls, params: DeleteParams[types.TId]) -> None:
        async with params['c'].AsyncSession() as session:
            try:
                await cls._SERVICE.delete({
                    'admin': cls._ADMIN,
                    'c': params['c'],
                    'session': session,
                    'id': params['id'],
                    'authorized_user_id': params['authorization']._user_id,
                })
            except base_service.NotFoundError as e:
                raise
            except Exception as e:
                raise

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
