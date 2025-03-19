from sqlmodel import SQLModel
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel.ext.asyncio.session import AsyncSession

from gallery.models.pagination import Pagination
from typing import Protocol, Unpack, TypeVar, TypedDict, Generic


class Id(TypedDict):
    pass


class Table[T: 'Table', TId](SQLModel):

    @classmethod
    def _build_get_by_id_query(cls, id: TId) -> SelectOfScalar[T]:
        raise NotImplementedError

    @classmethod
    async def _get_by_id(cls, session: AsyncSession, id: TId) -> T | None:
        return (await session.exec(cls._build_get_by_id_query(id))).one_or_none()

    def build_pagination(self, query: SelectOfScalar[T], pagination: Pagination):
        return query.offset(pagination.offset).limit(pagination.limit)


'''
P = typing.ParamSpec('P')
R = typing.TypeVar('R')
TDB = typing.TypeVar('TDB', bound='BaseDB[typing.Any]')

IdType = typing.TypeVar(
    'IdType', bound=typing.Union[str | int, tuple[str | int, ...]])


class Id(typing.Generic[IdType]):
    def __init__(self, fields: list[str]):
        self.fields = fields

    def get(self, obj) -> IdType:
        if len(self.fields) == 1:
            return getattr(obj, self.fields[0])
        return tuple(getattr(obj, field) for field in self.fields)

    def generate(self) -> IdType:
        if len(self.fields) == 1:
            return str(uuid.uuid4())
        return tuple(str(uuid.uuid4()) for _ in self.fields)


class IdObject[IdType: typing.Any]:
    ID_COLS: typing.ClassVar[list[str]] = ['id']

    @property
    def _id(self) -> IdType:
        """Return the ID of the model"""

        if len(self.ID_COLS) > 1:
            return tuple(getattr(self, key) for key in self.ID_COLS)
        else:
            return getattr(self, self.ID_COLS[0])

    @classmethod
    def generate_id(cls) -> IdType:
        """Generate a new ID for the model"""

        if len(cls.ID_COLS) > 1:
            return tuple(str(uuid.uuid4()) for _ in range(len(cls.ID_COLS)))
        else:
            return str(uuid.uuid4())

    @classmethod
    def export_plural_to_dict(cls, items: collections.abc.Iterable[typing.Self]) -> dict[IdType, typing.Self]:
        return {item._id: item for item in items}


class BaseDB[IdType](DeclarativeBase, IdObject[IdType]):
    pass


class OrderBy[T](BaseModel):
    field: T
    ascending: bool


class ApiMethodParamsBase(typing.TypedDict):
    session: AsyncSession
    c: client.Client
    authorized_user_id: typing.NotRequired[types.User.id]
    admin: typing.NotRequired[bool]


class ApiMethodParamsBaseWithId[IdType](ApiMethodParamsBase):
    id: IdType


class ApiMethodParamsCustom[T](typing.TypedDict):
    db_inst: T


class ApiPostParams[TPostModel: BaseModel](ApiMethodParamsBase):
    create_model: TPostModel


class ApiPostParamsCustom[T, TPostModel: BaseModel](ApiPostParams[TPostModel], ApiMethodParamsCustom[T]):
    pass


class ApiGetParams[IdType](ApiMethodParamsBaseWithId[IdType]):
    pass


class ApiGetParamsCustom[T, IdType](ApiGetParams[IdType], ApiMethodParamsCustom[T]):
    pass


class ApiPatchParams[IdType, TPatchModel: BaseModel](ApiMethodParamsBaseWithId[IdType]):
    update_model: TPatchModel


class ApiPatchParamsCustom[T, IdType, TPatchModel: BaseModel](ApiPatchParams[IdType, TPatchModel], ApiMethodParamsCustom[T]):
    pass


class ApiDeleteParams[IdType](ApiMethodParamsBaseWithId[IdType]):
    pass


class ApiDeleteParamsCustom[T, IdType](ApiDeleteParams[IdType], ApiMethodParamsCustom[T]):
    pass


class CheckAuthorizationExistingParams[IdType, T: BaseDB](ApiMethodParamsBase):
    inst: T
    method: typing.Literal['get', 'patch', 'delete']







class TableService[
    T: BaseDB[typing.Any],
    IdType: dict,
    TAddModel: BaseModel,
    TUpdateModel: BaseModel,
    TApiGetParams,
    TOrderBy
]:

    _ROUTER_TAG: typing.ClassVar[str] = 'asdf'
    BASE_DB: T

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

    @classmethod
    async def _check_authorization_existing(cls, **kwargs: typing.Unpack[CheckAuthorizationExistingParams[IdType, T]]) -> None:
        """Check if the user is authorized to access the instance"""
        pass

    @classmethod
    async def _check_authorization_new(cls, **kwargs: typing.Unpack[ApiPostParams[TAddModel]]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def _check_validation_delete(cls, **kwargs: typing.Unpack[ApiDeleteParams[IdType]]) -> None:
        """Check if the user is authorized to delete the instance"""
        pass

    @classmethod
    async def _check_validation_patch(cls, **kwargs: typing.Unpack[ApiPatchParams[IdType, TUpdateModel]]) -> None:
        """Check if the user is authorized to update the instance"""
        pass

    @classmethod
    async def _check_validation_post(cls, **kwargs: typing.Unpack[ApiPostParams[TAddModel]]) -> None:
        """Check if the user is authorized to create a new instance"""
        pass

    @classmethod
    async def _get(cls, session: AsyncSession, id: IdType) -> T | None:
        """Get an instance of the model by ID, don't overwrite this method"""

        query: Select[T] = select(cls)
        if len(cls.BASE_DB.ID_COLS) == 1:
            id = [id]
        for i, col in enumerate(cls.BASE_DB.ID_COLS):
            field: InstrumentedAttribute = getattr(cls.BASE_DB, col)
            query = query.where(field == id[i])

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def api_get(cls, params: ApiGetParams[IdType], **kwargs: Unpack[TApiGetParams]) -> T:
        """Used in conjunction with API endpoints, raises exceptions while trying to get an instance of the model by ID"""

        reveal_type(params)
        reveal_type(kwargs)

        inst = await cls._get(params['session'], params['id'])
        if not inst:
            raise cls.not_found_exception()
        # await cls._check_authorization_existing(**kwargs, inst=inst, method='get')
        # await cls.api_get_custom(**kwargs, db_inst=inst)
        return inst

    @classmethod
    async def api_get_custom(cls, params, **kwargs: Unpack[TApiGetParams]) -> None:
        """Functionality to run after getting an instance of the model by ID but before returning"""
        pass

    @classmethod
    async def api_post(cls, **kwargs: Unpack[ApiPostParams[TAddModel]]) -> T:
        """Used in conjunction with API endpoints, raises exceptions while trying to create a new instance of the model"""

        await cls._check_authorization_new(**kwargs)
        await cls._check_validation_post(**kwargs)

        db_inst = await cls.db_inst_from_add_model(**kwargs)
        await cls.api_post_custom(**kwargs)

        kwargs['session'].add(db_inst)
        await kwargs['session'].commit()
        await kwargs['session'].refresh(db_inst)
        return db_inst

    @classmethod
    async def db_inst_from_add_model(cls, **kwargs: Unpack[ApiPostParams[TAddModel]]) -> T:
        """Create a new instance of the model from the create model (TAddModel), don't overwrite this method"""
        return cls.BASE_DB(**kwargs['create_model'].model_dump())

    @classmethod
    async def api_post_custom(cls, **kwargs: Unpack[ApiPostParamsCustom[T, TAddModel]]) -> None:
        """Functionality to run after creating a new instance of the model but before returning"""
        pass

    @classmethod
    async def api_patch(cls, **kwargs: Unpack[ApiPatchParams[IdType, TUpdateModel]]) -> T:
        """Used in conjunction with API endpoints, raises exceptions while trying to update an instance of the model by ID"""

        db_inst = await cls._get(kwargs['session'], kwargs['id'])
        if not db_inst:
            raise cls.not_found_exception()

        await cls._check_authorization_existing(**kwargs, inst=db_inst, method='patch')
        await cls._check_validation_patch(**kwargs)

        await cls.update_db_inst_from_update_model(db_inst, **kwargs)
        await cls.api_patch_custom(**kwargs, db_inst=db_inst)

        await kwargs['session'].commit()
        await kwargs['session'].refresh(db_inst)
        return db_inst

    @classmethod
    async def update_db_inst_from_update_model(cls, db_inst: T, **kwargs: typing.Unpack[ApiPatchParams[IdType, TUpdateModel]]) -> None:
        """Update an instance of the model from the update model (TUpdateModel)"""
        for key, value in kwargs['update_model'].model_dump(exclude_unset=True).items():
            setattr(db_inst, key, value)

    @classmethod
    async def api_patch_custom(cls, **kwargs: typing.Unpack[ApiPatchParamsCustom[T, IdType, TUpdateModel]]) -> None:
        """Functionality to run after updating an instance of the model but before returning"""
        pass

    @classmethod
    async def api_delete(cls, **kwargs: typing.Unpack[ApiDeleteParams[IdType]]) -> None:
        """Used in conjunction with API endpoints, raises exceptions while trying to delete an instance of the model by ID"""

        inst = await cls._get(kwargs['session'], kwargs['id'])
        if not inst:
            raise cls.not_found_exception()

        await cls._check_authorization_existing(**kwargs, inst=inst, method='delete')
        await cls._check_validation_delete(**kwargs)

        await cls.api_delete_custom(**kwargs, inst=inst)

        await cls._delete(kwargs['session'], kwargs['id'])
        await kwargs['session'].commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @classmethod
    async def api_delete_custom(cls, **kwargs: typing.Unpack[ApiDeleteParamsCustom[T, IdType]]) -> None:
        """Functionality to run after deleting an instance of the model but before returning"""
        pass

    @classmethod
    async def _delete(cls, session: AsyncSession, id: IdType):
        """delete the instance by id, don't overwrite this method"""

        stmt = delete(cls.BASE_DB)
        if len(cls.BASE_DB.ID_COLS) == 1:
            id = [id]
        for i, col in enumerate(cls.BASE_DB.ID_COLS):
            field: InstrumentedAttribute = getattr(cls.BASE_DB, col)
            stmt = stmt.where(field == id[i])
        return await session.execute(stmt)

'''
