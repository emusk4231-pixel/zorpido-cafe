from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
	path('download/<int:image_id>/', views.download_image, name='download_image'),
]