# coding: utf-8

from django.conf import settings

from django.core.files.storage import get_storage_class

from storages.backends.s3boto import S3BotoStorage


# based in: http://django-compressor.readthedocs.org/en/1.3/remote-storages/
#           https://github.com/pricco/django-staticfiles-configuration/

class CachedS3BotoStorage(S3BotoStorage):

    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def exists(self, name):
        return self.local_storage.exists(name)

    def _save(self, name, content):
        name = super(CachedS3BotoStorage, self)._save(name, content)
        self.local_storage._save(name, content)
        return name

    def _open(self, name, mode='rb'):
        return self.local_storage._open(name, mode)


class StaticCachedS3BotoStorage(CachedS3BotoStorage):

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.AWS_STATIC_LOCATION

        super(StaticCachedS3BotoStorage, self).__init__(*args, **kwargs)


class MediaS3BotoStorage(S3BotoStorage):

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.AWS_MEDIA_LOCATION

        super(MediaS3BotoStorage, self).__init__(*args, **kwargs)
