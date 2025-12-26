from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('accounts/', include('users.urls')),
    path('pos/', include('pos.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('blogs/', include('blogs.urls')),
    path('gallery/', include('gallery.urls')),
]

from django.core.files.storage import default_storage

# Only serve MEDIA files via Django's static helper when using filesystem
# storage (typically local development). When using Cloudinary the media
# URLs are served by Cloudinary CDN and Django should not attempt to
# expose `MEDIA_URL` via static() in production.
if settings.DEBUG or getattr(settings, 'DEFAULT_FILE_STORAGE', '').startswith('django'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Zorpido Admin Panel"
admin.site.site_title = "Zorpido Admin"
admin.site.index_title = "Welcome to Zorpido Management System"