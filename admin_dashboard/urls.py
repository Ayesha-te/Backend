from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('reports/', views.reports_view, name='reports'),
    path('api/stats/', views.dashboard_stats_api, name='stats_api'),
    path('api/export/', views.export_data, name='export_data'),
]