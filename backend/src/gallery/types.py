from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config
from pymongo import collection

# types of documents in the database
type DocumentId = str

# types of files
type MediaId = str
type MediaType = typing.Literal['image', 'video', 'audio']
type ImageId = str
type VideoId = str
type AudioId = str
type MediaIdType = ImageId | VideoId | AudioId

type StudioId = str
type EventId = str

type VersionId = str
type SizeId = str

type HexColor = str
type FileEnding = str
type AcceptableFileEndings = set[FileEnding]
type Filename = str
