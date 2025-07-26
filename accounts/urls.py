from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, UserDetail, BookingList, VehicleList, DocumentList
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetail.as_view(), name='user-detail'),
    path('bookings/', BookingList.as_view(), name='booking-list'),
    path('vehicles/', VehicleList.as_view(), name='vehicle-list'),
    path('documents/', DocumentList.as_view(), name='document-list'),
]
