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
type StudioPrivateId = str
type EventId = str
type EventPrivateId = str
type MediaId = str
type MediaPrivateId = str

type ImageFileId = str
type ImageFilePrivateId = str
type VideoFileId = str
type VideoFilePrivateId = str
type ImageGroupId = str
type ImageGroupPrivateId = str

type VersionId = str
type SizeId = str
type GroupId = str
type MediaName = str


type HexColor = str
type FileEnding = str
type AcceptableFileEndings = set[FileEnding]
type Filename = str
