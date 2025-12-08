<<<<<<< HEAD
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Zorpido Admin Panel"
admin.site.site_title = "Zorpido Admin"
=======
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Zorpido Admin Panel"
admin.site.site_title = "Zorpido Admin"
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
admin.site.index_title = "Welcome to Zorpido Management System"