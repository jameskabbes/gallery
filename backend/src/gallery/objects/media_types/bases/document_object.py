from gallery.objects.db import document_object
from gallery import types
from gallery.objects import media_types


class Types:
    media_type = str
    event_id = types.EventId


class DocumentObject:
    event_id: Types.event_id
    media_type: Types.media_type
