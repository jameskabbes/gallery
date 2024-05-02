from typing import TypedDict, Optional, Union
import pydantic
import typing
import datetime as datetime_module
import re
from gallery import config

DocumentId = str

ImageId = DocumentId
ImageGroupId = DocumentId
EventId = DocumentId
VideoId = DocumentId

ImageGroupName = str
ImageVersionId = str
ImageSizeId = str

HexColor = str
FileEnding = str
