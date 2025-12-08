<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='list'),
    path('cigarettes/', views.special_list, {'kind': 'cigarettes'}, name='cigarettes'),
    path('drinks/', views.special_list, {'kind': 'drinks'}, name='drinks'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('item/<slug:slug>/', views.item_detail, name='item'),
=======
from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='list'),
    path('cigarettes/', views.special_list, {'kind': 'cigarettes'}, name='cigarettes'),
    path('drinks/', views.special_list, {'kind': 'drinks'}, name='drinks'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('item/<slug:slug>/', views.item_detail, name='item'),
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
]