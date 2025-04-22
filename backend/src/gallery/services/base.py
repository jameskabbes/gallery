from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Protocol, Unpack, TypeVar, TypedDict, Generic, NotRequired, Literal, Self, ClassVar, Type
from pydantic import BaseModel
from .. import client, types
from ..schemas.pagination import Pagination
from .. import models

T = TypeVar('T', bound=SQLModel, covariant=False)
TId = TypeVar('TId', bound=types._IdType, covariant=False)
TCreateModel = TypeVar('TCreateModel', bound=BaseModel, default=BaseModel)
TUpdateModel = TypeVar('TUpdateModel', bound=BaseModel, default=BaseModel)


class CRUDParamsBase(TypedDict):
    session: AsyncSession
    c: client.Client
    authorized_user_id: NotRequired[types.User.id]
    admin: NotRequired[bool]


class WithId[TId: types._IdType](TypedDict):
    id: TId


class WithTableInst[T:SQLModel](TypedDict):
    table_inst: T


class CreateParams(Generic[TCreateModel], CRUDParamsBase):
    create_model: TCreateModel


class AfterCreateParams(
        Generic[T, TCreateModel], CreateParams[TCreateModel], WithId[types._IdType], WithTableInst[T]):
    pass


class ReadParams(Generic[TId], CRUDParamsBase, WithId[TId]):
    pass


class AfterReadParams(Generic[T, TId], ReadParams[TId], WithTableInst[T]):
    pass


class UpdateParams(Generic[TId, TUpdateModel], CRUDParamsBase, WithId[TId]):
    update_model: TUpdateModel


class AfterUpdateParams(Generic[T, TId, TUpdateModel], UpdateParams[TId, TUpdateModel], WithTableInst[T]):
    pass


class DeleteParams(Generic[TId], CRUDParamsBase, WithId[TId]):
    pass


class AfterDeleteParams(Generic[T, TId], DeleteParams[TId], WithTableInst[T]):
    pass


class CheckAuthorizationExistingParams(Generic[T], CRUDParamsBase):
    inst: T
    method: Literal['get', 'patch', 'delete']


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


class HasTableInstFromCreateModel(Generic[T, TCreateModel], models.HasTable[T]):
    @classmethod
    async def table_inst_from_create_model(cls, create_model: TCreateModel) -> T:
        """Create a new instance of the model from the create model (TCreateModel), don't overwrite this method"""
        ...


class Service(
    Generic[
        T,
        TId,
        TCreateModel,
        TUpdateModel,
        TAfterCreateCustomParams,
        TAfterReadCustomParams,
        TAfterUpdateCustomParams,
        TAfterDeleteCustomParams
    ],
    HasTableInstFromCreateModel[T, TCreateModel],
):

    @classmethod
    def table_id(cls, inst: T) -> TId:
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def _build_select_by_id(cls, id: TId) -> SelectOfScalar[T]:
        """Build a select statement to get an instance of the model by ID"""
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    async def _get_by_id(cls, session: AsyncSession, id: TId) -> T | None:
        return (await session.exec(cls._build_select_by_id(id))).one_or_none()

    @classmethod
    async def _get_by_id_with_exception(cls, session: AsyncSession, id: TId) -> T:
        inst = await cls._get_by_id(session, id)
        if not inst:
            raise ValueError(cls.__class__.__name__ +
                             ' with id ' + str(id) + ' not found')
        return inst

    def build_pagination(self, query: SelectOfScalar[T], pagination: Pagination):
        return query.offset(pagination.offset).limit(pagination.limit)

    async def _delete(self, session: AsyncSession):
        await session.delete(self)

    @classmethod
    async def _check_authorization_existing(cls, params: CheckAuthorizationExistingParams[T]) -> None:
        """Check if the user is authorized to access the instance"""
        pass

    @classmethod
    async def _check_authorization_new(cls, params: CreateParams[TCreateModel]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def _check_validation_delete(cls, params: DeleteParams[TId]) -> None:
        """Check if the user is authorized to delete the instance"""
        pass

    @classmethod
    async def _check_validation_patch(cls, params: UpdateParams[TId, TUpdateModel]) -> None:
        """Check if the user is authorized to update the instance"""
        pass

    @classmethod
    async def _check_validation_post(cls, params: CreateParams[TCreateModel]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def read(cls, params: ReadParams[TId], custom_params: TAfterReadCustomParams = {}) -> T:
        """Used in conjunction with API endpoints, raises exceptions while trying to get an instance of the model by ID"""

        inst = await cls._get_by_id_with_exception(params['session'], params['id'])

        check_auth_params: CheckAuthorizationExistingParams[T] = {
            'session': params['session'],
            'c': params['c'],
            'inst': inst,
            'method': 'get'
        }

        if 'authorized_user_id' in params:
            check_auth_params['authorized_user_id'] = params['authorized_user_id']

        if 'admin' in params:
            check_auth_params['admin'] = params['admin']

        await cls._check_authorization_existing(check_auth_params)

        after_read_params: AfterReadParams[T, TId] = {
            'session': params['session'],
            'c': params['c'],
            'table_inst': inst,
            'id': params['id']
        }

        if 'authorized_user_id' in params:
            after_read_params['authorized_user_id'] = params['authorized_user_id']

        if 'admin' in params:
            after_read_params['admin'] = params['admin']

        await cls._after_read(after_read_params, custom_params)
        return inst

    @classmethod
    async def _after_read(cls, params: AfterReadParams[T, TId], custom_params: TAfterReadCustomParams = {}) -> None:
        """Functionality to run after getting an instance of the model by ID but before returning"""
        pass

    @classmethod
    async def create(cls, params: CreateParams[TCreateModel], custom_params: TAfterCreateCustomParams = {}) -> T:
        """Used in conjunction with API endpoints, raises exceptions while trying to create a new instance of the model"""

        await cls._check_authorization_new(params)
        await cls._check_validation_post(params)

        table_inst = await cls.table_inst_from_create_model(params['create_model'])

        await cls._after_create({**params, 'table_inst': table_inst, 'id': cls.table_id(table_inst)}, custom_params)

        params['session'].add(table_inst)
        await params['session'].commit()
        await params['session'].refresh(table_inst)
        return table_inst

    @classmethod
    async def table_inst_from_create_model(cls, create_model: TCreateModel) -> T:
        return cls._TABLE(**create_model.model_dump())

    @classmethod
    async def _after_create(cls, params: AfterCreateParams[T, TCreateModel], custom_params: TAfterCreateCustomParams = {}) -> None:
        """Functionality to run after creating a new instance of the model but before returning"""
        pass

    @classmethod
    async def update(cls, params: UpdateParams[TId, TUpdateModel], custom_params: TAfterUpdateCustomParams = {}) -> T:
        """Used in conjunction with API endpoints, raises exceptions while trying to update an instance of the model by ID"""

        inst = await cls._get_by_id_with_exception(params['session'], params['id'])

        check_auth_params: CheckAuthorizationExistingParams[T] = {
            'session': params['session'],
            'c': params['c'],
            'inst': inst,
            'method': 'get'
        }

        if 'authorized_user_id' in params:
            check_auth_params['authorized_user_id'] = params['authorized_user_id']

        if 'admin' in params:
            check_auth_params['admin'] = params['admin']

        await cls._check_authorization_existing(check_auth_params)
        await cls._check_validation_patch(params)
        await cls._update_table_inst(inst, params['update_model'])

        after_update_params: AfterUpdateParams[T, TId, TUpdateModel] = {
            'session': params['session'],
            'c': params['c'],
            'table_inst': inst,
            'id': params['id'],
            'update_model': params['update_model']
        }

        if 'authorized_user_id' in params:
            after_update_params['authorized_user_id'] = params['authorized_user_id']
        if 'admin' in params:
            after_update_params['admin'] = params['admin']

        await cls._after_update(after_update_params, custom_params)

        await params['session'].commit()
        await params['session'].refresh(inst)
        return inst

    @classmethod
    async def _update_table_inst(cls, table_inst: T, update_model: TUpdateModel) -> None:
        """Update an instance of the model from the update model (TUpdateModel)"""

        for key, value in update_model.model_dump(exclude_unset=True).items():
            setattr(table_inst, key, value)

    @classmethod
    async def _after_update(cls, params: AfterUpdateParams[T, TId, TUpdateModel], custom_params: TAfterUpdateCustomParams = {}) -> None:
        """Functionality to run after updating an instance of the model but before returning"""
        pass

    @classmethod
    async def delete(cls, params: DeleteParams[TId], custom_params: TAfterDeleteCustomParams = {}) -> None:
        """Used in conjunction with API endpoints, raises exceptions while trying to delete an instance of the model by ID"""

        inst = await cls._get_by_id_with_exception(params['session'], params['id'])

        check_auth_params = CheckAuthorizationExistingParams[T](
            session=params['session'],
            c=params['c'],
            inst=inst,
            method='get'
        )

        if 'authorized_user_id' in params:
            check_auth_params['authorized_user_id'] = params['authorized_user_id']

        if 'admin' in params:
            check_auth_params['admin'] = params['admin']

        await cls._check_authorization_existing(check_auth_params)
        await cls._check_validation_delete(params)

        await params['session'].delete(inst)

        after_delete_params: AfterDeleteParams[T, TId] = {
            'session': params['session'],
            'c': params['c'],
            'table_inst': inst,
            'id': params['id']
        }

        if 'authorized_user_id' in params:
            after_delete_params['authorized_user_id'] = params['authorized_user_id']
        if 'admin' in params:
            after_delete_params['admin'] = params['admin']

        await cls._after_delete(after_delete_params, custom_params)

        await params['session'].commit()

    @classmethod
    async def _after_delete(cls, params: AfterDeleteParams[T, TId], custom_params: TAfterDeleteCustomParams = {}) -> None:
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
