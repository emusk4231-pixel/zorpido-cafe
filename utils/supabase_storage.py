"""
Lightweight storage helper that uses Django's default storage backend.

This module preserves the previous `upload_file` / `get_file_url` API so
other parts of the codebase don't need to change. It no longer depends on
Supabase and will store files using `default_storage` (MEDIA_ROOT or any
configured storage backend).
"""
from typing import Optional
import logging

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def upload_file(file_obj, file_name: str, bucket: Optional[str] = None) -> str:
    """Save file_obj to Django's `default_storage` and return a public URL/path.

    - `file_obj` may be a file-like object or bytes.
    - `file_name` is the desired path within storage (e.g. 'profile_pictures/user.jpg').
    - `bucket` is optional and will be prepended as a folder name when present.
    """
    if bucket:
        file_name = f"{bucket.rstrip('/')}/{file_name.lstrip('/')}"

    # Normalize data
    if hasattr(file_obj, 'read'):
        data = file_obj.read()
    elif isinstance(file_obj, (bytes, bytearray)):
        data = file_obj
    else:
        raise ValueError('file_obj must be file-like or bytes')

    if isinstance(data, str):
        data = data.encode('utf-8')

    # Save using default_storage
    try:
        # `default_storage.save` expects a File or path+ContentFile
        path = default_storage.save(file_name, ContentFile(data))
        try:
            return default_storage.url(path)
        except Exception:
            # Some storage backends may not implement `url` the same way; fall back to MEDIA_URL
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            if not media_url.endswith('/'):
                media_url = media_url + '/'
            return f"{media_url}{path.lstrip('/')}"
    except Exception:
        logger.exception('Failed to save file via default_storage')
        raise


def get_file_url(file_name: str, bucket: Optional[str] = None, signed: bool = False, expires: int = 3600) -> str:
    """Return a URL for a file saved through `default_storage`.

    This intentionally ignores `signed` and `expires` because signed URL
    generation is backend-specific; if you require signed URLs, configure
    a storage backend that supports them and call its API directly.
    """
    if bucket:
        path = f"{bucket.rstrip('/')}/{file_name.lstrip('/')}"
    else:
        path = file_name

    try:
        return default_storage.url(path)
    except Exception:
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if not media_url.endswith('/'):
            media_url = media_url + '/'
        return f"{media_url}{path.lstrip('/')}"
