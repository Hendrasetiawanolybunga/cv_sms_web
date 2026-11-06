from django.urls import path
from . import views

urlpatterns = [
    # Area Publik (Katalog B2B & Direct WhatsApp Order)
    path('', views.home, name='home'),

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
    path('dashboard/products/images/<int:pk>/delete/', views.dashboard_product_image_delete, name='dashboard_product_image_delete'),

    # Profil Perusahaan (Pengaturan Publik & Operasional Pabrik)
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),
    path('dashboard/settings/company_profile/', views.dashboard_settings, name='dashboard_settings_company_profile'),

    # Pengguna Internal Staff/Admin CRUD
    path('dashboard/users/', views.dashboard_user_list, name='dashboard_user_list'),
    path('dashboard/users/create/', views.dashboard_user_create, name='dashboard_user_create'),
    path('dashboard/users/<int:user_id>/edit/', views.dashboard_user_edit, name='dashboard_user_edit'),
    path('dashboard/users/<int:user_id>/toggle/', views.dashboard_user_toggle, name='dashboard_user_toggle'),

    # Backend Endpoints Transaksi, Rekening, & Pelanggan (Disimpan untuk internal/arsip)
    path('dashboard/orders/', views.dashboard_order_list, name='dashboard_order_list'),
    path('dashboard/orders/create/', views.dashboard_order_create, name='dashboard_order_create'),
    path('dashboard/orders/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),
    path('dashboard/orders/<int:order_id>/status/', views.dashboard_order_status_update, name='dashboard_order_status_update'),
    path('dashboard/orders/<int:order_id>/delete/', views.dashboard_order_delete, name='dashboard_order_delete'),
    path('dashboard/banks/', views.dashboard_bank_list, name='dashboard_bank_list'),
    path('dashboard/banks/create/', views.dashboard_bank_create, name='dashboard_bank_create'),
    path('dashboard/banks/<int:bank_id>/edit/', views.dashboard_bank_edit, name='dashboard_bank_edit'),
    path('dashboard/banks/<int:bank_id>/toggle/', views.dashboard_bank_toggle, name='dashboard_bank_toggle'),
    path('dashboard/banks/<int:bank_id>/delete/', views.dashboard_bank_delete, name='dashboard_bank_delete'),
    path('dashboard/customers/', views.dashboard_customer_list, name='dashboard_customer_list'),
    path('dashboard/customers/create/', views.dashboard_customer_create, name='dashboard_customer_create'),
    path('dashboard/customers/<int:customer_id>/', views.dashboard_customer_detail, name='dashboard_customer_detail'),
    path('dashboard/customers/<int:customer_id>/edit/', views.dashboard_customer_edit, name='dashboard_customer_edit'),
    path('dashboard/customers/<int:customer_id>/delete/', views.dashboard_customer_delete, name='dashboard_customer_delete'),
    path('dashboard/customers/<int:customer_id>/toggle/', views.dashboard_customer_toggle, name='dashboard_customer_toggle'),
]
