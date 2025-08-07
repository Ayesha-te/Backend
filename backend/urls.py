from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def root_view(request):
    return JsonResponse({"message": "Welcome to the Access Auto Services API!"})

def favicon_view(request):
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site URL
    path('admin-dashboard/', include('admin_dashboard.urls')),  # Custom admin dashboard
    path('', root_view),               # Root URL for a quick test message
    path('favicon.ico', favicon_view), # Handle favicon requests
    path('api/accounts/', include('accounts.urls')),
    path('api/dvla/', include('DVLAA.urls')),
    path('api/paypal/', include(('PAYPAL.urls', 'PAYPAL'), namespace='paypal')),
    path('api/email/', include('email_service.urls')),
    path('api/', include('admin_api.urls')),  # Admin panel API endpoints
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
