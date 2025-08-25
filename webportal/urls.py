from django.urls import path
from . import views

urlpatterns = [
    # Live
    path('', views.live_traffic, name='live-traffic'),
    path('live/traffic/', views.live_traffic, name='live-traffic'),
    path('live/traffic/data/', views.live_traffic_data, name='live-traffic-data'),
    path('live/sessions/', views.live_sessions, name='live-sessions'),
    path('live/sessions/data/', views.live_sessions_data, name='live-sessions-data'),
    
    # Centre Detail (placeholder)
    path('centre/<int:centre_id>/', views.centre_detail, name='centre-detail'),
    
    # Reports
    path('reports/centres/', views.reports_centres, name='reports-centres'),
    path('reports/centres/<int:centre_id>/', views.reports_centre_detail, name='reports-centre-detail'),
    path('reports/centres/<int:centre_id>/<int:language_id>/', views.reports_language_detail, name='reports-language-detail'),
    path('reports/centres/<int:centre_id>/<int:language_id>/<int:operator_id>/', views.reports_agent_detail, name='reports-agent-detail'),
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
    
    # Admin Administrators CRUD
    path('admin/administrators/', views.admin_administrators, name='admin-administrators'),
    path('admin/administrators/create/', views.admin_administrators_create, name='admin-administrators-create'),
    path('admin/administrators/<int:administrator_id>/edit/', views.admin_administrators_edit, name='admin-administrators-edit'),
    path('admin/administrators/<int:administrator_id>/delete/', views.admin_administrators_delete, name='admin-administrators-delete'),
    
    # Admin Payments CRUD
    path('admin/payments/', views.admin_payments, name='admin-payments'),
    path('admin/payments/create/', views.admin_payments_create, name='admin-payments-create'),
    path('admin/payments/<int:payplan_id>/edit/', views.admin_payments_edit, name='admin-payments-edit'),
    path('admin/payments/<int:payplan_id>/delete/', views.admin_payments_delete, name='admin-payments-delete'),
]
