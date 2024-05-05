import typing
from pymongo import collection, results, database
from gallery import types, config, utils
import pydantic


ChildIdType = typing.TypeVar('ChildIdType', bound=types.DocumentId)


class DocumentObject(pydantic.BaseModel, typing.Generic[ChildIdType]):

    id: ChildIdType = pydantic.Field(alias=config.DOCUMENT_ID_KEY)

    @ classmethod
    def find_by_id(cls, collection: collection.Collection, id: types.DocumentId) -> typing.Self | None:
        """Load a document from the database by its id. If the document does not exist, return None."""

        result = collection.find_one({config.DOCUMENT_ID_KEY: id})
        if result is None:
            return None
        return cls(**result)

    def update_all(self, collection: collection.Collection) -> results.UpdateResult:
        """Update the document in the database."""
        return collection.update_one({config.DOCUMENT_ID_KEY: self.id}, {
            '$set': self.model_dump(by_alias=True)})

    def update_fields(self, collection: collection.Collection, fields: set[str]) -> results.UpdateResult:
        return collection.update_one(
            {config.DOCUMENT_ID_KEY: self.id}, {'$set': self.model_dump(by_alias=True, include=fields, exclude_defaults=True)})

    def insert(self, collection: collection.Collection) -> results.UpdateResult:
        """Insert the document into the database."""
        return collection.insert_one(self.model_dump(
            by_alias=True))

    @staticmethod
    def exists(collection: collection.Collection, id: ChildIdType) -> bool:
        """Check if the document's id exists in the database."""
        return collection.find_one({config.DOCUMENT_ID_KEY: id}) is not None

    @classmethod
    def generate_id(cls) -> ChildIdType:
        """Generate a new id for a document."""
        return utils.generate_nanoid()
