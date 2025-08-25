from django.urls import path
from . import views

app_name = 'thedjangolook'

urlpatterns = [
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/create/', views.agent_create, name='agent_create'),
    path('agents/<int:agent_id>/', views.agent_detail, name='agent_detail'),
    path('agents/<int:agent_id>/update/', views.agent_update, name='agent_update'),
    path('agents/<int:agent_id>/delete/', views.agent_delete, name='agent_delete'),
]
