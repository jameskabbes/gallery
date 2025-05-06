from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Protocol, Unpack, TypeVar, TypedDict, Generic, NotRequired, Literal, Self, ClassVar, Type, Optional
from pydantic import BaseModel
from .. import client, types
from ..schemas.pagination import Pagination
from .. import models

TCreateModel = TypeVar('TCreateModel', bound=BaseModel, default=BaseModel)
TCreateModel_contra = TypeVar(
    'TCreateModel_contra', bound=BaseModel, default=BaseModel, contravariant=True)
TCreateModel_co = TypeVar(
    'TCreateModel_co', bound=BaseModel, default=BaseModel, covariant=True)

TUpdateModel = TypeVar('TUpdateModel', bound=BaseModel, default=BaseModel)
TUpdateModel_contra = TypeVar(
    'TUpdateModel_contra', bound=BaseModel, default=BaseModel, contravariant=True)
TUpdateModel_co = TypeVar('TUpdateModel_co', bound=BaseModel,
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


class AfterCreateParams(
        Generic[models.TModel_contra, TCreateModel_contra], CreateParams[TCreateModel_contra], WithId[types._IdType], WithModelInst[models.TModel_contra]):
    pass


class ReadParams(Generic[types.TId], CRUDParamsBase, WithId[types.TId]):
    pass


class AfterReadParams(Generic[models.TModel_contra, types.TId], ReadParams[types.TId], WithModelInst[models.TModel_contra]):
    pass


class UpdateParams(Generic[types.TId, TUpdateModel_contra], CRUDParamsBase, WithId[types.TId]):
    update_model: TUpdateModel_contra


class AfterUpdateParams(Generic[models.TModel_contra, types.TId, TUpdateModel_contra], UpdateParams[types.TId, TUpdateModel_contra], WithModelInst[models.TModel_contra]):
    pass


class DeleteParams(Generic[types.TId], CRUDParamsBase, WithId[types.TId]):
    pass


class AfterDeleteParams(Generic[models.TModel_contra, types.TId], DeleteParams[types.TId], WithModelInst[models.TModel_contra]):
    pass


class CheckAuthorizationExistingParams(Generic[models.TModel_contra, types.TId], CRUDParamsBase, WithId[types.TId], WithModelInst[models.TModel_contra]):
    method: Literal['get', 'patch', 'delete']


class CheckAuthorizationNewParams(Generic[TCreateModel_contra], CreateParams[TCreateModel_contra]):
    pass


class CheckValidationDeleteParams(Generic[types.TId], DeleteParams[types.TId]):
    pass


class CheckValidationPatchParams(Generic[models.TModel, types.TId, TUpdateModel_contra], UpdateParams[types.TId, TUpdateModel_contra], WithModelInst[models.TModel]):
    pass


class CheckValidationPostParams(Generic[TCreateModel_contra], CreateParams[TCreateModel_contra]):
    pass


class AfterCreateCustomParams(TypedDict):
    pass


class AfterReadCustomParams(TypedDict):
    pass


class AfterUpdateCustomParams(TypedDict):
    pass


class AfterDeleteCustomParams(TypedDict):
    pass


TAfterCreateCustomParams = TypeVar(
    'TAfterCreateCustomParams', bound=AfterCreateCustomParams, default=AfterCreateCustomParams)
TAfterReadCustomParams = TypeVar(
    'TAfterReadCustomParams', bound=AfterReadCustomParams, default=AfterReadCustomParams)
TAfterUpdateCustomParams = TypeVar(
    'TAfterUpdateCustomParams', bound=AfterUpdateCustomParams, default=AfterUpdateCustomParams)
TAfterDeleteCustomParams = TypeVar(
    'TAfterDeleteCustomParams', bound=AfterDeleteCustomParams, default=AfterDeleteCustomParams)


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
    Generic[models.TModelSimple, types.TIdSimple],
    HasModel[models.TModelSimple],
    HasModelId[models.TModelSimple, types.TIdSimple],
    HasBuildSelectById[models.TModelSimple, types.TIdSimple],
):

    _MODEL: Type[models.TModelSimple]

    @classmethod
    def model_id(cls, inst: models.TModelSimple) -> types.TIdSimple:
        return inst.id  # type: ignore

    @classmethod
    def _build_select_by_id(cls, id: types.TIdSimple) -> SelectOfScalar[models.TModelSimple]:
        return select(cls._MODEL).where(cls._MODEL.id == id)


class NotFoundError(Exception):
    def __init__(self, model: Type[models.Model], id: types._IdType):
        raise ValueError(model.__class__.__name__ +
                         ' with id ' + str(id) + ' not found')


class AlreadyExistsError(Exception):
    def __init__(self, model: Type[models.Model], id: types._IdType):
        raise ValueError(
            model.__class__.__name__ + ' with id ' + str(id) + ' already exists')


class NotAvailableError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class Service(
    Generic[
        models.TModel,
        types.TId,
        TCreateModel,
        TUpdateModel,
        TAfterCreateCustomParams,
        TAfterReadCustomParams,
        TAfterUpdateCustomParams,
        TAfterDeleteCustomParams
    ],
    HasModel[models.TModel],
    HasModelInstFromCreateModel[models.TModel, TCreateModel],
    HasModelId[models.TModel, types.TId],
    HasBuildSelectById[models.TModel, types.TId],
):

    @classmethod
    async def _get_by_id(cls, session: AsyncSession, id: types.TId) -> models.TModel | None:
        return (await session.exec(cls._build_select_by_id(id))).one_or_none()

    @classmethod
    async def _get_by_id_with_exception(cls, session: AsyncSession, id: types.TId) -> models.TModel:
        inst = await cls._get_by_id(session, id)
        if not inst:
            raise NotFoundError(cls._MODEL, id)
        return inst

    @classmethod
    def build_pagination(cls, query: SelectOfScalar[models.TModel], pagination: Pagination):
        return query.offset(pagination.offset).limit(pagination.limit)

    async def _delete(self, session: AsyncSession):
        await session.delete(self)

    @classmethod
    async def _check_authorization_existing(cls, params: CheckAuthorizationExistingParams[models.TModel, types.TId]) -> None:
        """Check if the user is authorized to access the instance"""
        pass

    @classmethod
    async def _check_authorization_new(cls, params: CheckAuthorizationNewParams[TCreateModel]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def _check_validation_delete(cls, params: CheckValidationDeleteParams[types.TId]) -> None:
        """Check if the user is authorized to delete the instance"""
        pass

    @classmethod
    async def _check_validation_patch(cls, params: CheckValidationPatchParams[models.TModel, types.TId, TUpdateModel]) -> None:
        """Check if the user is authorized to update the instance"""
        pass

    @classmethod
    async def _check_validation_post(cls, params: CheckValidationPostParams[TCreateModel]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def read(cls, params: ReadParams[types.TId], custom_params: TAfterReadCustomParams = {}) -> models.TModel:
        """Used in conjunction with API endpoints, raises exceptions while trying to get an instance of the model by ID"""

        model_inst = await cls._get_by_id_with_exception(params['session'], params['id'])

        await cls._check_authorization_existing(
            {**params, 'model_inst': model_inst, 'method': 'get'})

        await cls._after_read({
            **params, 'model_inst': model_inst}, custom_params)
        return model_inst

    @classmethod
    async def _after_read(cls, params: AfterReadParams[models.TModel, types.TId], custom_params: TAfterReadCustomParams = {}) -> None:
        """Functionality to run after getting an instance of the model by ID but before returning"""
        pass

    @classmethod
    async def create(cls, params: CreateParams[TCreateModel], custom_params: TAfterCreateCustomParams = {}) -> models.TModel:
        """Used in conjunction with API endpoints, raises exceptions while trying to create a new instance of the model"""

        await cls._check_authorization_new(params)
        await cls._check_validation_post(params)

        model_inst = cls.model_inst_from_create_model(params['create_model'])

        await cls._after_create({**params, 'model_inst': model_inst, 'id': cls.model_id(model_inst)}, custom_params)

        params['session'].add(model_inst)
        await params['session'].commit()
        await params['session'].refresh(model_inst)
        return model_inst

    @classmethod
    def model_inst_from_create_model(cls, create_model: TCreateModel) -> models.TModel:
        return cls._MODEL(**create_model.model_dump())

    @classmethod
    async def _after_create(cls, params: AfterCreateParams[models.TModel, TCreateModel], custom_params: TAfterCreateCustomParams = {}) -> None:
        """Functionality to run after creating a new instance of the model but before returning"""
        pass

    @classmethod
    async def update(cls, params: UpdateParams[types.TId, TUpdateModel], custom_params: TAfterUpdateCustomParams = {}) -> models.TModel:
        """Used in conjunction with API endpoints, raises exceptions while trying to update an instance of the model by ID"""

        model_inst = await cls._get_by_id_with_exception(params['session'], params['id'])

        await cls._check_authorization_existing({
            'session': params['session'],
            'c': params['c'],
            'model_inst': model_inst,
            'method': 'get',
            'id': params['id'],
            'admin': params['admin'],
            'authorized_user_id': params['authorized_user_id']
        })
        await cls._check_validation_patch({**params, 'model_inst': model_inst})
        await cls._update_model_inst(model_inst, params['update_model'])

        await cls._after_update({
            **params, 'model_inst': model_inst}, custom_params)

        await params['session'].commit()
        await params['session'].refresh(model_inst)
        return model_inst

    @classmethod
    async def _update_model_inst(cls, inst: models.TModel, update_model: TUpdateModel) -> None:
        """Update an instance of the model from the update model (TUpdateModel)"""

        inst.sqlmodel_update(update_model.model_dump(exclude_unset=True))

    @classmethod
    async def _after_update(cls, params: AfterUpdateParams[models.TModel, types.TId, TUpdateModel], custom_params: TAfterUpdateCustomParams = {}) -> None:
        """Functionality to run after updating an instance of the model but before returning"""
        pass

    @classmethod
    async def delete(cls, params: DeleteParams[types.TId], custom_params: TAfterDeleteCustomParams = {}) -> None:
        """Used in conjunction with API endpoints, raises exceptions while trying to delete an instance of the model by ID"""

        model_inst = await cls._get_by_id_with_exception(params['session'], params['id'])

        await cls._check_authorization_existing({
            'session': params['session'],
            'c': params['c'],
            'method': 'delete',
            'id': params['id'],
            'model_inst': model_inst,
            'admin': params['admin'],
            'authorized_user_id': params['authorized_user_id']
        })
        await cls._check_validation_delete(params)
        await params['session'].delete(model_inst)
        await cls._after_delete({
            **params, 'model_inst': model_inst}, custom_params)

        await params['session'].commit()

    @classmethod
    async def _after_delete(cls, params: AfterDeleteParams[models.TModel, types.TId], custom_params: TAfterDeleteCustomParams = {}) -> None:
        """Functionality to run after deleting an instance of the model but before returning"""
        pass


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
