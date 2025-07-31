from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({"message": "Welcome to the backend API!"})

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site URL
    path('', root_view),               # Root URL for a quick test message
    path('api/accounts/', include('accounts.urls')),
   
    path('api/dvla/', include('DVLAA.urls')),
    path('api/paypal/', include('PAYPAL.urls')),
]
