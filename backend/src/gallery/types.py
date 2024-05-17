from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config
from pymongo import collection

# types of documents in the database
# types of files
type MediaType = typing.Literal['image', 'video', 'audio']

type ImageId = str
type VideoId = str
type AudioId = str
type MediaId = ImageId | VideoId | AudioId

type StudioId = str
type EventId = str
type DocumentId = MediaId | StudioId | EventId

type VersionId = str
type SizeId = str

type HexColor = str
type FileEnding = str
type AcceptableFileEndings = set[FileEnding]
type Filename = str
