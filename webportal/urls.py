from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Live
    path('live/traffic/', views.live_traffic, name='live-traffic'),
    path('live/sessions/', views.live_sessions, name='live-sessions'),
    
    # Reports
    path('reports/centres/', views.reports_centres, name='reports-centres'),
    path('reports/friends/', views.reports_friends, name='reports-friends'),
    path('reports/historical/', views.reports_historical, name='reports-historical'),
    
    # Admin Centres CRUD
    path('admin/centres/', views.admin_centres, name='admin-centres'),
    path('admin/centres/create/', views.admin_centres_create, name='admin-centres-create'),
    path('admin/centres/<int:centre_id>/edit/', views.admin_centres_edit, name='admin-centres-edit'),
    path('admin/centres/<int:centre_id>/delete/', views.admin_centres_delete, name='admin-centres-delete'),
    
    # Admin Operators CRUD
    path('admin/operators/', views.admin_operators, name='admin-operators'),
    path('admin/operators/create/', views.admin_operators_create, name='admin-operators-create'),
    path('admin/operators/<int:operator_id>/edit/', views.admin_operators_edit, name='admin-operators-edit'),
    path('admin/operators/<int:operator_id>/delete/', views.admin_operators_delete, name='admin-operators-delete'),
    
    # Admin
    path('admin/administrators/', views.admin_administrators, name='admin-administrators'),
    path('admin/payments/', views.admin_payments, name='admin-payments'),
]
