from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='list'),
    path('cigarettes/', views.special_list, {'kind': 'cigarettes'}, name='cigarettes'),
    path('drinks/', views.special_list, {'kind': 'drinks'}, name='drinks'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('item/<slug:slug>/', views.item_detail, name='item'),
]