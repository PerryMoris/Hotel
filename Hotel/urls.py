from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

admin.site.site_title = "Hotel Management System"
admin.site.site_header = "HRM administration"
admin.site.index_title = "HRM administration"

urlpatterns = [
    path('admin/', admin.site.urls, name="adminpage"),
    path('', include('hmsys.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)