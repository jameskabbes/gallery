from gallery.objects.media.video import file as video_file
from gallery.objects.media.bases import version as base_version


class Model(base_version.Version[video_file.File]):
    pass


class Version(Model):
    pass
