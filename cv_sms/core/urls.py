from django.urls import path
from . import views

urlpatterns = [
    # Area Publik & Toko
    path('', views.home, name='home'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<str:order_code>/', views.order_detail, name='order_detail'),

    # Auth & Profil Pelanggan
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/orders/', views.customer_orders, name='customer_orders'),

    # Area Dashboard Admin
    path('dashboard/', views.dashboard_index, name='dashboard_index'),
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),

    # Produk CRUD
    path('dashboard/products/', views.dashboard_product_list, name='dashboard_product_list'),
    path('dashboard/products/create/', views.dashboard_product_create, name='dashboard_product_create'),
    path('dashboard/products/<int:product_id>/edit/', views.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/products/<int:product_id>/toggle/', views.dashboard_product_toggle, name='dashboard_product_toggle'),
    path('dashboard/products/<int:product_id>/delete/', views.dashboard_product_delete, name='dashboard_product_delete'),

    # Pesanan / Transaksi CRUD
    path('dashboard/orders/', views.dashboard_order_list, name='dashboard_order_list'),
    path('dashboard/orders/create/', views.dashboard_order_create, name='dashboard_order_create'),
    path('dashboard/orders/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),
    path('dashboard/orders/<int:order_id>/status/', views.dashboard_order_status_update, name='dashboard_order_status_update'),
    path('dashboard/orders/<int:order_id>/delete/', views.dashboard_order_delete, name='dashboard_order_delete'),

    # Profil Perusahaan (Pengaturan Publik)
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),

    # Rekening Bank CRUD
    path('dashboard/banks/', views.dashboard_bank_list, name='dashboard_bank_list'),
    path('dashboard/banks/create/', views.dashboard_bank_create, name='dashboard_bank_create'),
    path('dashboard/banks/<int:bank_id>/edit/', views.dashboard_bank_edit, name='dashboard_bank_edit'),
    path('dashboard/banks/<int:bank_id>/toggle/', views.dashboard_bank_toggle, name='dashboard_bank_toggle'),
    path('dashboard/banks/<int:bank_id>/delete/', views.dashboard_bank_delete, name='dashboard_bank_delete'),

    # Pelanggan CRUD
    path('dashboard/customers/', views.dashboard_customer_list, name='dashboard_customer_list'),
    path('dashboard/customers/create/', views.dashboard_customer_create, name='dashboard_customer_create'),
    path('dashboard/customers/<int:customer_id>/', views.dashboard_customer_detail, name='dashboard_customer_detail'),
    path('dashboard/customers/<int:customer_id>/edit/', views.dashboard_customer_edit, name='dashboard_customer_edit'),
    path('dashboard/customers/<int:customer_id>/delete/', views.dashboard_customer_delete, name='dashboard_customer_delete'),
    path('dashboard/customers/<int:customer_id>/toggle/', views.dashboard_customer_toggle, name='dashboard_customer_toggle'),

    # Pengguna Internal Staff/Admin CRUD
    path('dashboard/users/', views.dashboard_user_list, name='dashboard_user_list'),
    path('dashboard/users/create/', views.dashboard_user_create, name='dashboard_user_create'),
    path('dashboard/users/<int:user_id>/edit/', views.dashboard_user_edit, name='dashboard_user_edit'),
    path('dashboard/users/<int:user_id>/toggle/', views.dashboard_user_toggle, name='dashboard_user_toggle'),
]

