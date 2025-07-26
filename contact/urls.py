from django.urls import path
from .views import ContactMessageCreateView

urlpatterns = [
    path('send/', ContactMessageCreateView.as_view(), name='contact-send'),
]
