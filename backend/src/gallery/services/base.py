from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Protocol, Unpack, TypeVar, TypedDict, Generic, NotRequired, Literal, Self, ClassVar, Type, Optional
from pydantic import BaseModel
from .. import client, types
from ..schemas.pagination import Pagination
from .. import models
from collections.abc import Sequence

TCreateModel = TypeVar(
    'TCreateModel', bound=BaseModel, default=BaseModel)
TCreateModel_contra = TypeVar(
    'TCreateModel_contra', bound=BaseModel, default=BaseModel, contravariant=True)
TCreateModel_co = TypeVar(
    'TCreateModel_co', bound=BaseModel, default=BaseModel, covariant=True)

TUpdateModelService = TypeVar(
    'TUpdateModelService', bound=BaseModel, default=BaseModel)
TUpdateModelService_contra = TypeVar(
    'TUpdateModelService_contra', bound=BaseModel, default=BaseModel, contravariant=True)
TUpdateModelService_co = TypeVar('TUpdateModelService_co', bound=BaseModel,
                                 default=BaseModel, covariant=True)


class CRUDParamsBase(TypedDict):
    session: AsyncSession
    c: client.Client
    authorized_user_id: Optional[types.User.id]
    admin: bool


class WithId(Generic[types.TId], TypedDict):
    id: types.TId


class WithModelInst(Generic[models.TModel_contra], TypedDict):
    model_inst: models.TModel_contra


class CreateParams(Generic[TCreateModel_contra], CRUDParamsBase):
    create_model: TCreateModel_contra


class ReadParams(Generic[types.TId], CRUDParamsBase, WithId[types.TId]):
    pass


class ReadManyParams(CRUDParamsBase):
    pagination: Pagination


class UpdateParams(Generic[types.TId, TUpdateModelService_contra], CRUDParamsBase, WithId[types.TId]):
    update_model: TUpdateModelService_contra


class DeleteParams(Generic[types.TId], CRUDParamsBase, WithId[types.TId]):
    pass


CheckAuthorizationExistingOperation = Literal['read', 'update', 'delete']


class CheckAuthorizationExistingParams(Generic[models.TModel_contra, types.TId], CRUDParamsBase, WithId[types.TId], WithModelInst[models.TModel_contra]):
    operation: CheckAuthorizationExistingOperation


class CheckAuthorizationNewParams(Generic[TCreateModel_contra], CreateParams[TCreateModel_contra]):
    pass


class CheckAuthorizationReadManyParams(ReadManyParams):
    pass


class CheckValidationDeleteParams(Generic[types.TId], DeleteParams[types.TId]):
    pass


class CheckValidationPatchParams(Generic[models.TModel, types.TId, TUpdateModelService_contra], UpdateParams[types.TId, TUpdateModelService_contra], WithModelInst[models.TModel]):
    pass


class CheckValidationPostParams(Generic[TCreateModel_contra], CreateParams[TCreateModel_contra]):
    pass


class HasModel(Protocol[models.TModel_co]):
    _MODEL: Type[models.TModel_co]


class HasModelInstFromCreateModel(Protocol[models.TModel_co, TCreateModel_contra]):
    @classmethod
    def model_inst_from_create_model(cls, create_model: TCreateModel_contra) -> models.TModel_co:
        ...


class HasModelId(Protocol[models.TModel_contra, types.TId_co]):
    @classmethod
    def model_id(cls, inst: models.TModel_contra) -> types.TId_co:
        ...


class HasBuildSelectById(Protocol[models.TModel, types.TId_contra]):
    @classmethod
    def _build_select_by_id(cls, id: types.TId_contra) -> SelectOfScalar[models.TModel]:
        ...


class SimpleIdModelService(
    Generic[models.TSimpleModel, types.TSimpleId],
    HasModel[models.TSimpleModel],
    HasModelId[models.TSimpleModel, types.TSimpleId],
    HasBuildSelectById[models.TSimpleModel, types.TSimpleId],
):

    _MODEL: Type[models.TSimpleModel]

    @classmethod
    def model_id(cls, inst: models.TSimpleModel) -> types.TSimpleId:
        return inst.id  # type: ignore

    @classmethod
    def _build_select_by_id(cls, id: types.TSimpleId) -> SelectOfScalar[models.TSimpleModel]:
        return select(cls._MODEL).where(cls._MODEL.id == id)


class ServiceError(Exception):
    error_message: str

    def __init__(self, error_message: str):
        self.error_message = error_message
        raise Exception(error_message)


class NotFoundError(ValueError, ServiceError):

    def __init__(self, model: Type[models.Model], id: types.Id):
        self.error_message = NotFoundError.not_found_message(model, id)

        raise ValueError(self.error_message)

    @staticmethod
    def not_found_message(model: Type[models.Model], id: types.Id) -> str:
        return model.__class__.__name__ + ' with id ' + str(id) + ' not found'


class AlreadyExistsError(ServiceError):
    def __init__(self, model: Type[models.Model], id: types.Id):
        self.error_message = model.__class__.__name__ + \
            ' with id ' + str(id) + ' already exists'
        raise ValueError(self.error_message)


class NotAvailableError(ServiceError):
    pass


class UnauthorizedError(ServiceError):
    pass


class Service(
    Generic[
        models.TModel,
        types.TId,
        TCreateModel,
        TUpdateModelService,
    ],
    HasModel[models.TModel],
    HasModelInstFromCreateModel[models.TModel, TCreateModel],
    HasModelId[models.TModel, types.TId],
    HasBuildSelectById[models.TModel, types.TId],

):

    @classmethod
    async def fetch_by_id(cls, session: AsyncSession, id: types.TId) -> models.TModel | None:
        return (await session.exec(cls._build_select_by_id(id))).one_or_none()

    @classmethod
    async def fetch_many(cls, session: AsyncSession, pagination: Pagination) -> Sequence[models.TModel]:
        query = select(cls._MODEL).offset(
            pagination.offset).limit(pagination.limit)
        return (await session.exec(query)).all()

    @classmethod
    async def fetch_by_id_with_exception(cls, session: AsyncSession, id: types.TId) -> models.TModel:
        inst = await cls.fetch_by_id(session, id)
        if inst is None:
            raise NotFoundError(cls._MODEL, id)
        return inst

    @classmethod
    async def _check_authorization_existing(cls, params: CheckAuthorizationExistingParams[models.TModel, types.TId]) -> None:
        """Check if the user is authorized to access the instance"""
        pass

    @classmethod
    async def _check_authorization_new(cls, params: CheckAuthorizationNewParams[TCreateModel]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def _check_authorization_read_many(cls, params: CheckAuthorizationReadManyParams) -> None:
        """Check if the user is authorized to read many instances"""
        pass

    @classmethod
    async def _check_validation_delete(cls, params: CheckValidationDeleteParams[types.TId]) -> None:
        """Check if the user is authorized to delete the instance"""
        pass

    @classmethod
    async def _check_validation_patch(cls, params: CheckValidationPatchParams[models.TModel, types.TId, TUpdateModelService]) -> None:
        """Check if the user is authorized to update the instance"""
        pass

    @classmethod
    async def _check_validation_post(cls, params: CheckValidationPostParams[TCreateModel]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def read(cls, params: ReadParams[types.TId]) -> models.TModel:
        """Used in conjunction with API endpoints, raises exceptions while trying to get an instance of the model by ID"""

        model_inst = await cls.fetch_by_id_with_exception(params['session'], params['id'])

        await cls._check_authorization_existing(
            {**params, 'model_inst': model_inst, 'operation': 'read'})

        return model_inst

    @classmethod
    async def read_many(cls, params: ReadManyParams) -> Sequence[models.TModel]:
        """Used in conjunction with API endpoints, raises exceptions while trying to get a list of instances of the model"""

        await cls._check_authorization_read_many(params)
        return await cls.fetch_many(params['session'], params['pagination'])

    @classmethod
    async def create(cls, params: CreateParams[TCreateModel]) -> models.TModel:
        """Used in conjunction with API endpoints, raises exceptions while trying to create a new instance of the model"""

        await cls._check_authorization_new(params)
        await cls._check_validation_post(params)

        model_inst = cls.model_inst_from_create_model(params['create_model'])

        params['session'].add(model_inst)
        await params['session'].commit()
        await params['session'].refresh(model_inst)
        return model_inst

    @classmethod
    def model_inst_from_create_model(cls, create_model: TCreateModel) -> models.TModel:
        return cls._MODEL(**create_model.model_dump())

    @classmethod
    async def update(cls, params: UpdateParams[types.TId, TUpdateModelService]) -> models.TModel:
        """Used in conjunction with API endpoints, raises exceptions while trying to update an instance of the model by ID"""

        # when changing this, be sure to update the services/gallery.py file as well

        model_inst = await cls.fetch_by_id_with_exception(params['session'], params['id'])

        await cls._check_authorization_existing({
            'session': params['session'],
            'c': params['c'],
            'model_inst': model_inst,
            'operation': 'read',
            'id': params['id'],
            'admin': params['admin'],
            'authorized_user_id': params['authorized_user_id']
        })
        await cls._check_validation_patch({**params, 'model_inst': model_inst})
        await cls._update_model_inst(model_inst, params['update_model'])

        await params['session'].commit()
        await params['session'].refresh(model_inst)
        return model_inst

    @classmethod
    async def _update_model_inst(cls, inst: models.TModel, update_model: TUpdateModelService) -> None:
        """Update an instance of the model from the update model (TUpdateModelService)"""

        inst.sqlmodel_update(update_model.model_dump(exclude_unset=True))

    @classmethod
    async def delete(cls, params: DeleteParams[types.TId]) -> None:
        """Used in conjunction with API endpoints, raises exceptions while trying to delete an instance of the model by ID"""

        model_inst = await cls.fetch_by_id_with_exception(params['session'], params['id'])

        await cls._check_authorization_existing({
            'session': params['session'],
            'c': params['c'],
            'operation': 'delete',
            'id': params['id'],
            'model_inst': model_inst,
            'admin': params['admin'],
            'authorized_user_id': params['authorized_user_id']
        })
        await cls._check_validation_delete(params)
        await params['session'].delete(model_inst)
        await params['session'].commit()


'''


def generate(self) -> TId:
    if len(self.fields) == 1:
        return str(uuid.uuid4())
    return tuple(str(uuid.uuid4()) for _ in self.fields)



@classmethod
def export_plural_to_dict(cls, items: collections.abc.Iterable[typing.Self]) -> dict[TId, typing.Self]:
    return {item._id: item for item in items}




    @classmethod
    def make_order_by_dependency(cls):

        def order_by_depends(
                order_by: list[TOrderBy] = Query(
                    [], description='Ordered series of fields to sort the results by, in the order they should be applied'),
                order_by_desc: list[TOrderBy] = Query(
                    [], description='Unordered series of fields which should be sorted in a descending manner, must be a subset of "order_by" fields')
        ) -> list[OrderBy[TOrderBy]]:

            order_by_set = set(order_by)
            order_by_desc_set = set(order_by_desc)

            if not order_by_desc_set.issubset(order_by_set):
                raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                    detail='"order_by_desc" fields must be a subset of "order_by" fields')

            return [
                OrderBy[TOrderBy](
                    field=field, ascending=field not in order_by_desc_set)
                for field in order_by
            ]

        return order_by_depends

    # @classmethod
    # def _build_conditions(cls, filters: dict[str, typing.Any]):

    #     conditions = []
    #     for key in filters:
    #         value = filters[key]
    #         field: InstrumentedAttribute = getattr(cls, key)

    #         if isinstance(value, list):
    #             conditions.append(field.in_(value))
    #         else:
    #             conditions.append(field == value)

    #     return and_(*conditions)

    # @classmethod
    # def _build_order_by[TQuery: Select, TOrderBy](cls, query: TQuery, order_by: list[OrderBy[TOrderBy]]):
    #     for order in order_by:
    #         field: InstrumentedAttribute = getattr(cls, order.field)
    #         if order.ascending:
    #             query = query.order_by(field.asc())
    #         else:
    #             query = query.order_by(field.desc())

    #     return query


'''
