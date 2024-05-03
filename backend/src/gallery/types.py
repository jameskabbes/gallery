from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config
from pymongo import collection

DocumentId = str
VersionId = str
SizeId = str
GroupId = str
EventId = DocumentId
MediaName = str

ImageId = DocumentId
ImageGroupId = DocumentId
VideoId = DocumentId

ImageGroupName = MediaName
VideoName = MediaName

DbCollections = dict[str, collection.Collection]

HexColor = str
FileEnding = str
AcceptableFileEndings = set[FileEnding]
Filename = str
