from django.conf import settings
from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage


class MediaS3BotoStorage(S3BotoStorage):
    bucket_name = settings.MEDIA_BUCKET_NAME

    """
    S3 storage backend that saves the files locally, too.
    """
