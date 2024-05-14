from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config
from pymongo import collection

# types of documents in the database
type DocumentId = str
type PrivateDocumentId = str

type StudioId = str
type EventId = str

type ImageFileId = str
type VideoFileId = str
type ImageGroupId = str
type ImageGroupName = str

type MediaId = ImageFileId | VideoFileId | ImageGroupId
type MediaType = typing.Literal['image.file', 'image.group', 'video.file']
type MediaCoreType = typing.Literal['image', 'video']

type VersionId = str
type SizeId = str

type HexColor = str
type FileEnding = str
type AcceptableFileEndings = set[FileEnding]
type Filename = str
