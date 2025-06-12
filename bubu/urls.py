from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),  # Default Django admin URL
    path('', include('edward.urls')),  # Main app URL
    path('custom-admin/', include('edward.urls')),  # Optional custom admin paths, if needed
    path('api/', include('edward.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
