import typing
from pymongo import collection, results, database
from gallery import types, config, utils
import pydantic
import nanoid
from abc import ABC, abstractmethod

# class DocumentObject[IdType: types.DocumentId](pydanctic.BaseModel):


class DocumentObject[IdType: types.DocumentId, IdentifyingKeysType](pydantic.BaseModel):

    # currently a bug in pydantic in handling nested type aliases: https://github.com/pydantic/pydantic/issues/8984
    # for now, just redefine the ID alias in every child of DocumentObject
    ID_KEY: typing.ClassVar[str] = config.DOCUMENT_ID_KEY
    id: IdType = pydantic.Field(alias=ID_KEY)

    IDENTIFYING_KEYS_TYPE: typing.ClassVar
    IDENTIFYING_KEYS: typing.ClassVar[tuple[IdentifyingKeysType]]

    class Config:
        arbitrary_types_allowed = True

    @ classmethod
    def make_from_id_keys(cls, id_keys: tuple) -> typing.Self:
        return cls(**{**{id_key: id_keys[i] for i, id_key in enumerate(cls.IDENTIFYING_KEYS)}, **{cls.ID_KEY: cls.generate_id()}})

    @ classmethod
    def delete_by_id(cls, collection: collection.Collection, id: IdType) -> results.DeleteResult:
        """Delete a document from the database by its id."""
        return collection.delete_one({cls.ID_KEY: id})

    @ classmethod
    def get(cls, collection: collection.Collection, filter: dict = {}, projection: dict = {}) -> typing.Self | None:
        """Load all documents from the database that match the filter."""
        result = collection.find_one(filter, projection=projection)
        if result == None:
            return None
        return cls(**result)

    @classmethod
    def get_by_id(cls, collection: collection.Collection, id: IdType, projection: dict = {}) -> typing.Self | None:
        """Load a document from the database by its id. If the document does not exist, return None."""
        return cls.get(collection, {cls.ID_KEY: id}, projection)

    def update_all_fields(self, collection: collection.Collection) -> results.UpdateResult:
        """Update the document in the database."""
        return collection.update_one({self.ID_KEY: self.id}, {
            '$set': self.model_dump(by_alias=True, exclude_defaults=True)})

    def update_fields(self, collection: collection.Collection, fields: set[str]) -> results.UpdateResult:
        return collection.update_one(
            {self.ID_KEY: self.id}, {'$set': self.model_dump(by_alias=True, include=fields)})

    def insert(self, collection: collection.Collection) -> results.UpdateResult:
        """Insert the document into the database."""
        return collection.insert_one(self.model_dump(
            by_alias=True, exclude_defaults=True))

    @ classmethod
    def exists(cls, collection: collection.Collection, id: IdType) -> bool:
        """Check if the document's id exists in the database."""
        return collection.find_one({cls.ID_KEY: id}) is not None

    @classmethod
    def generate_id(cls) -> IdType:
        """Generate a new id for a document."""
        return nanoid.generate(config.NANOID_ALPHABET, config.NANOID_SIZE)
