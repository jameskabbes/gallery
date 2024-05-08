import typing
from pymongo import collection, results, database
from gallery import types, config, utils
import pydantic

# class DocumentObject[IdType: types.DocumentId](pydanctic.BaseModel):


class DocumentObject[IdType: types.DocumentId, PrivateIdType: types.PrivateDocumentId](pydantic.BaseModel):

    # currently a bug in pydantic in handling nested type aliases: https://github.com/pydantic/pydantic/issues/8984
    # for now, just redefine the ID alias in every child of DocumentObject
    id: IdType = pydantic.Field(alias=config.DOCUMENT_ID_KEY)
    private_id: PrivateIdType

    class Config:
        arbitrary_types_allowed = True

    def delete(self, collection: collection.Collection) -> results.DeleteResult:
        """Delete the document from the database."""
        return collection.delete_one({config.DOCUMENT_ID_KEY: self.id})

    @ classmethod
    def delete_by_id(cls, collection: collection.Collection, id: IdType) -> results.DeleteResult:
        """Delete a document from the database by its id."""
        return collection.delete_one({config.DOCUMENT_ID_KEY: id})

    @ classmethod
    def find_by_id(cls, collection: collection.Collection, id: IdType, projection: dict = {}) -> typing.Self | None:
        """Load a document from the database by its id. If the document does not exist, return None."""
        return cls.find(collection, {config.DOCUMENT_ID_KEY: id}, projection)

    @ classmethod
    def find(cls, collection: collection.Collection, filter: dict = {}, projection: dict = {}) -> typing.Self | None:
        """Load all documents from the database that match the filter."""
        result = collection.find_one(filter, projection=projection)
        if result is None:
            return None
        return cls(**result)

    def update_all_fields(self, collection: collection.Collection) -> results.UpdateResult:
        """Update the document in the database."""
        return collection.update_one({config.DOCUMENT_ID_KEY: self.id}, {
            '$set': self.model_dump(by_alias=True, exclude_defaults=True)})

    def update_fields(self, collection: collection.Collection, fields: set[str]) -> results.UpdateResult:
        return collection.update_one(
            {config.DOCUMENT_ID_KEY: self.id}, {'$set': self.model_dump(by_alias=True, include=fields)})

    def insert(self, collection: collection.Collection) -> results.UpdateResult:
        """Insert the document into the database."""
        return collection.insert_one(self.model_dump(
            by_alias=True, exclude_defaults=True))

    @ staticmethod
    def exists(collection: collection.Collection, id: IdType) -> bool:
        """Check if the document's id exists in the database."""
        return collection.find_one({config.DOCUMENT_ID_KEY: id}) is not None

    @ classmethod
    def generate_id(cls) -> IdType:
        """Generate a new id for a document."""
        return utils.generate_nanoid()
