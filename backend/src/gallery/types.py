from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config

DocumentId = str
VersionId = str
SizeId = str
GroupId = str
EventId = DocumentId

ImageId = DocumentId
ImageGroupId = DocumentId
VideoId = DocumentId
VideoGroupId = DocumentId

ImageGroupName = str

HexColor = str
FileEnding = str
