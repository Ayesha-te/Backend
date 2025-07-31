from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    MyTokenObtainPairView,
    UserDetail,
    BookingList,
    VehicleList,
    DocumentList,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetail.as_view(), name='user_detail'),
    path('bookings/', BookingList.as_view(), name='user_bookings'),
    path('vehicles/', VehicleList.as_view(), name='user_vehicles'),
    path('documents/', DocumentList.as_view(), name='user_documents'),
]
