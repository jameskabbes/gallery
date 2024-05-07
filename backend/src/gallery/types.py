from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config
from pymongo import collection

# types of documents in the database
type DocumentId = str

type StudioId = DocumentId
type EventId = DocumentId
type MediaId = DocumentId


type VersionId = str
type SizeId = str
type GroupId = str
type MediaName = str

type ImageId = DocumentId
type ImageGroupId = DocumentId
type VideoId = DocumentId

type ImageGroupName = MediaName
type VideoName = MediaName

type DbCollections = dict[str, collection.Collection]

type HexColor = str
type FileEnding = str
type AcceptableFileEndings = set[FileEnding]
type Filename = str
