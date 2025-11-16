# messaging_app/messaging_app/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the chats app URLs under the 'api/' namespace
    path('api/', include('chats.urls')),
    
    # Add DRF's built-in auth URLs (for login/logout on the browsable API)
    path('api-auth/', include('rest_framework.urls')),
]