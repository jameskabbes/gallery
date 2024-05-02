from gallery.objects.media.image import file as image_file
from gallery.objects.media.bases import version as base_version


class Version(base_version.Version[image_file.File]):
    pass
