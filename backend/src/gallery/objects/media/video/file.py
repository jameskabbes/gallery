from gallery import types, config
import pydantic
import re
import datetime as datetime_module


class Types:
    id = types.VideoId
    event_id = types.EventId
    datetime = datetime_module.datetime
    name = str
    file_ending = types.FileEnding


class Init:
    id = Types.id
    event_id = Types.event_id
    datetime = Types.datetime | None
    name = Types.name
    file_ending = types.FileEnding


class Model(pydantic.BaseModel):

    id: Init.id = pydantic.Field(alias='_id')
    event_id: Init.event_id
    datetime: Init.datetime = pydantic.Field(default=None)
    name: Init.name
    file_ending: Init.file_ending


class File(Model):
    pass
