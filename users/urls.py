<<<<<<< HEAD
from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'users'

urlpatterns = [
    # (Email verification disabled)
    # Password reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    path('register/', views.customer_register, name='register'),
    path('login/', views.customer_login, name='login'),
    # New, cleaner staff login path
    path('staff/login/', views.staff_login, name='staff_login'),
    # Backwards-compatible redirect from old path
    path('staff-login/', RedirectView.as_view(pattern_name='users:staff_login', permanent=False)),
    path('logout/', views.customer_logout, name='logout'),
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('dashboard/export/profile_pdf/', views.export_my_profile_pdf, name='export_my_profile_pdf'),
    path('dashboard/status/', views.dashboard_status, name='dashboard_status'),
    path('dashboard/add-credit/', views.customer_add_deferred_credit, name='dashboard_add_credit'),
    path('dashboard/credit-history/', views.customer_credit_history, name='dashboard_credit_history'),
    path('profile/', views.customer_profile, name='profile'),
    path('orders/', views.customer_orders, name='orders'),
    # Staff customer management
    path('staff/customers/', views.staff_customer_list, name='staff_customer_list'),
    path('staff/customers/<int:pk>/edit/', views.staff_customer_edit, name='staff_customer_edit'),
    path('staff/customers/<int:pk>/adjust-credit/', views.staff_adjust_credit, name='staff_adjust_credit'),
=======
from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'users'

urlpatterns = [
    # (Email verification disabled)
    # Password reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    path('register/', views.customer_register, name='register'),
    path('login/', views.customer_login, name='login'),
    # New, cleaner staff login path
    path('staff/login/', views.staff_login, name='staff_login'),
    # Backwards-compatible redirect from old path
    path('staff-login/', RedirectView.as_view(pattern_name='users:staff_login', permanent=False)),
    path('logout/', views.customer_logout, name='logout'),
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('dashboard/export/profile_pdf/', views.export_my_profile_pdf, name='export_my_profile_pdf'),
    path('dashboard/status/', views.dashboard_status, name='dashboard_status'),
    path('dashboard/add-credit/', views.customer_add_deferred_credit, name='dashboard_add_credit'),
    path('dashboard/credit-history/', views.customer_credit_history, name='dashboard_credit_history'),
    path('profile/', views.customer_profile, name='profile'),
    path('orders/', views.customer_orders, name='orders'),
    # Staff customer management
    path('staff/customers/', views.staff_customer_list, name='staff_customer_list'),
    path('staff/customers/<int:pk>/edit/', views.staff_customer_edit, name='staff_customer_edit'),
    path('staff/customers/<int:pk>/adjust-credit/', views.staff_adjust_credit, name='staff_adjust_credit'),
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
]