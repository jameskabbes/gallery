from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config
from pymongo import collection

type DocumentId = str
type StudioId = DocumentId

type VersionId = str
type SizeId = str
type GroupId = str
type EventId = DocumentId
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
