<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
	path('download/<int:image_id>/', views.download_image, name='download_image'),
=======
from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
	path('download/<int:image_id>/', views.download_image, name='download_image'),
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
]