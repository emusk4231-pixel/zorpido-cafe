<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_dashboard, name='dashboard'),
    path('overview/', views.pos_overview, name='overview'),
    path('register/open/', views.open_register, name='open_register'),
    path('register/close/', views.close_register, name='close_register'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/add-item/', views.add_item_to_order, name='add_item'),
    path('order/<int:order_id>/remove-item/<int:item_id>/', views.remove_item_from_order, name='remove_item'),
    path('order/<int:order_id>/payment/', views.payment_screen, name='payment'),
    path('order/<int:order_id>/complete/', views.complete_payment, name='complete_payment'),
    path('created/', views.created_orders, name='created_orders'),
    path('order/<int:order_id>/complete-now/', views.complete_order, name='complete_order'),
    path('order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('completed/', views.completed_orders, name='completed_orders'),
    path('inventory/', views.inventory_management, name='inventory'),
    path('inventory/<int:item_id>/update/', views.update_stock, name='update_stock'),
    path('export/pdf/', views.export_pos_overview_pdf, name='export_pos_overview_pdf'),
    path('export/inventory/', views.export_inventory_pdf, name='export_inventory_pdf'),
    path('export/sales/', views.export_sales_pdf, name='export_sales_pdf'),
    path('export/customers/', views.export_customer_credit_pdf, name='export_customer_credit_pdf'),
    path('advanced-overview/', views.advanced_overview, name='advanced_overview'),
    path('api/overview-data/', views.api_overview_data, name='api_overview_data'),
    path('registers/<int:reg_id>/', views.register_detail, name='register_detail'),
    path('credit/', views.customer_credit_management, name='credit_management'),
    path('credit/<int:customer_id>/update/', views.update_customer_credit, name='update_credit'),
    path('credit/<int:customer_id>/history/', views.credit_history, name='credit_history'),
    # Expense Categories (admin-level)
    path('expenses/categories/', views.expense_category_list, name='expense_category_list'),
    path('expenses/categories/add/', views.expense_category_create, name='expense_category_create'),
    path('expenses/categories/<int:cat_id>/edit/', views.expense_category_edit, name='expense_category_edit'),
    path('expenses/categories/<int:cat_id>/delete/', views.expense_category_delete, name='expense_category_delete'),

    # Expenses CRUD
    path('expenses/', views.expense_list, name='expenses_list'),
    path('expenses/add/', views.expense_create, name='expense_add'),
    path('expenses/<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    path('expenses/by-category/', views.expenses_by_category, name='expenses_by_category'),
    # Seller management
    path('sellers/', views.seller_list, name='seller_list'),
    path('sellers/create/', views.seller_create, name='seller_create'),
    path('sellers/<int:seller_id>/', views.seller_detail, name='seller_detail'),
    path('sellers/<int:seller_id>/delete/', views.seller_delete, name='seller_delete'),
    path('sellers/<int:seller_id>/pay/', views.pay_seller_payable, name='seller_pay'),
    # Attendance endpoints
    # Attendance endpoints removed
=======
from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_dashboard, name='dashboard'),
    path('overview/', views.pos_overview, name='overview'),
    path('register/open/', views.open_register, name='open_register'),
    path('register/close/', views.close_register, name='close_register'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/add-item/', views.add_item_to_order, name='add_item'),
    path('order/<int:order_id>/remove-item/<int:item_id>/', views.remove_item_from_order, name='remove_item'),
    path('order/<int:order_id>/payment/', views.payment_screen, name='payment'),
    path('order/<int:order_id>/complete/', views.complete_payment, name='complete_payment'),
    path('created/', views.created_orders, name='created_orders'),
    path('order/<int:order_id>/complete-now/', views.complete_order, name='complete_order'),
    path('order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('completed/', views.completed_orders, name='completed_orders'),
    path('inventory/', views.inventory_management, name='inventory'),
    path('inventory/<int:item_id>/update/', views.update_stock, name='update_stock'),
    path('export/pdf/', views.export_pos_overview_pdf, name='export_pos_overview_pdf'),
    path('export/inventory/', views.export_inventory_pdf, name='export_inventory_pdf'),
    path('export/sales/', views.export_sales_pdf, name='export_sales_pdf'),
    path('export/customers/', views.export_customer_credit_pdf, name='export_customer_credit_pdf'),
    path('advanced-overview/', views.advanced_overview, name='advanced_overview'),
    path('api/overview-data/', views.api_overview_data, name='api_overview_data'),
    path('registers/<int:reg_id>/', views.register_detail, name='register_detail'),
    path('credit/', views.customer_credit_management, name='credit_management'),
    path('credit/<int:customer_id>/update/', views.update_customer_credit, name='update_credit'),
    path('credit/<int:customer_id>/history/', views.credit_history, name='credit_history'),
    path('expense/add/', views.add_expense, name='add_expense'),
    # Seller management
    path('sellers/', views.seller_list, name='seller_list'),
    path('sellers/create/', views.seller_create, name='seller_create'),
    path('sellers/<int:seller_id>/', views.seller_detail, name='seller_detail'),
    path('sellers/<int:seller_id>/delete/', views.seller_delete, name='seller_delete'),
    path('sellers/<int:seller_id>/pay/', views.pay_seller_payable, name='seller_pay'),
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
]