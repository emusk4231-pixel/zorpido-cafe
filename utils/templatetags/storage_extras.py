from django import template
from django.conf import settings
from django.core.files.storage import default_storage

register = template.Library()


@register.filter
def storage_url(value, bucket=None):
    """Resolve a stored file reference to an absolute URL.

    This returns:
    - the original value if it's already an absolute URL,
    - the value unchanged if it starts with '/', or
    - `default_storage.url()` when available, falling back to `MEDIA_URL`.
    """
    if not value:
        return ''
    s = str(value).strip()
    if s.startswith('http://') or s.startswith('https://'):
        return s
    if s.startswith('/'):
        return s

    if bucket:
        s = f"{bucket.rstrip('/')}/{s.lstrip('/')}"

    try:
        return default_storage.url(s)
    except Exception:
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if not media_url.endswith('/'):
            media_url = media_url + '/'
        return f"{media_url}{s.lstrip('/')}"

