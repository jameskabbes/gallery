import typing
from pymongo import collection as pymongo_collection, results, database
from gallery import types, config
from gallery.objects.bases import collection_object
import pydantic
import nanoid


class DocumentObject[IdType: types.DocumentId, IdentifyingKeysType](pydantic.BaseModel, collection_object.CollectionObject[IdType]):

    id: IdType = pydantic.Field(
        alias=collection_object.CollectionObject.ID_KEY)

    IDENTIFYING_KEYS_TYPE: typing.ClassVar = IdentifyingKeysType
    IDENTIFYING_KEYS: typing.ClassVar[tuple[IdentifyingKeysType]]
    PluralByIDType: typing.ClassVar[dict[IdType, typing.Self]]

    @ classmethod
    def get_by_id(cls, collection: pymongo_collection.Collection, id: IdType, projection: dict = {}) -> typing.Self | None:
        """Load a document from the database by its id. If the document does not exist, return None."""

        result = collection.find_one({cls.ID_KEY: id}, projection=projection)
        if result == None:
            return None
        else:
            return cls(**result)

    @ classmethod
    def find_id_keys_by_id(cls, collection: pymongo_collection.Collection, filter: dict = {}) -> dict[IdType, tuple[IdentifyingKeysType]]:
        return {i[cls.ID_KEY]: tuple(i[k] for k in cls.IDENTIFYING_KEYS) for i in collection.find(filter, projection={cls.ID_KEY: 1, **{k: 1 for k in cls.IDENTIFYING_KEYS}})}

    @classmethod
    def find_id_by_id_keys(cls, collection: pymongo_collection.Collection, filter: dict = {}) -> dict[tuple[IdentifyingKeysType], IdType]:

        id_by_id_keys: dict[tuple[IdentifyingKeysType], IdType] = {}

        id_and_id_keys = collection.find(filter, projection={**{
            ID_KEY: 1 for ID_KEY in cls.IDENTIFYING_KEYS}, **{cls.ID_KEY: 1}})

        for item in id_and_id_keys:
            print(item)
            id_keys_tuple = tuple(
                item[id_key] for id_key in cls.IDENTIFYING_KEYS)
            if id_keys_tuple in id_by_id_keys:
                raise ValueError(
                    f"Duplicate keys in db: {cls.IDENTIFYING_KEYS}={id_keys_tuple}")
            id_by_id_keys[id_keys_tuple] = item[cls.ID_KEY]

        return id_by_id_keys

    @classmethod
    def dict_id_keys_to_tuple(cls, id_keys: dict[IdentifyingKeysType]) -> tuple[IdentifyingKeysType]:
        return tuple(id_keys[k] for k in cls.IDENTIFYING_KEYS)

    @classmethod
    def id_keys_to_dict(cls, id_keys: tuple[IdentifyingKeysType]) -> dict[IdentifyingKeysType]:
        return {k: v for k, v in zip(cls.IDENTIFYING_KEYS, id_keys)}

    @ classmethod
    def make_from_id_keys(cls, id_keys: tuple) -> typing.Self:
        return cls(**{**{id_key: id_keys[i] for i, id_key in enumerate(cls.IDENTIFYING_KEYS)}, **{cls.ID_KEY: cls.generate_id()}})

    def update_all_fields(self, collection: pymongo_collection.Collection) -> results.UpdateResult:
        """Update the document in the database."""
        return collection.update_one({self.ID_KEY: self.id}, {
            '$set': self.model_dump(by_alias=True, exclude_defaults=True)})

    def update_fields(self, collection: pymongo_collection.Collection, fields: set[str]) -> results.UpdateResult:
        return collection.update_one(
            {self.ID_KEY: self.id}, {'$set': self.model_dump(by_alias=True, include=fields)})

    def insert(self, collection: pymongo_collection.Collection) -> results.UpdateResult:
        """Insert the document into the database."""
        return collection.insert_one(self.model_dump(
            by_alias=True, exclude_defaults=True))

    @ classmethod
    def generate_id(cls) -> IdType:
        """Generate a new id for a document."""
        return nanoid.generate(config.NANOID_ALPHABET, config.NANOID_SIZE)
