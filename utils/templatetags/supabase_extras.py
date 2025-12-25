from django import template
from utils.templatetags.storage_extras import storage_url as _storage_url

register = template.Library()

# Backwards-compatible shim: expose the new storage_url under the old name
register.filter('supabase_url', _storage_url)

def supabase_url(value, bucket=None):
    """Compatibility wrapper for older templates using `supabase_url`."""
    return _storage_url(value, bucket)
