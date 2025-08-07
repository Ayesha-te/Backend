from django.urls import path
from . import views, admin_views

urlpatterns = [
    # Admin Panel Access
    path('admin-panel/', admin_views.AdminPanelView.as_view(), name='admin-panel'),
    path('admin-dashboard/', admin_views.AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Users endpoints
    path('users/', views.UsersListView.as_view(), name='users-list'),
    path('users/count/', views.UsersCountView.as_view(), name='users-count'),
    
    # Bookings endpoints
    path('bookings/', views.BookingsListView.as_view(), name='bookings-list'),
    path('bookings/count/', views.BookingsCountView.as_view(), name='bookings-count'),
    path('bookings/trends/', views.BookingTrendsView.as_view(), name='booking-trends'),
    path('bookings/service-distribution/', views.ServiceDistributionView.as_view(), name='service-distribution'),
    
    # Payments endpoints
    path('payments/total/', views.PaymentsTotalView.as_view(), name='payments-total'),
    
    # Services endpoints
    path('services/', views.ServicesListView.as_view(), name='services-list'),
    
    # Vehicles endpoints
    path('vehicles/', views.VehiclesListView.as_view(), name='vehicles-list'),
]