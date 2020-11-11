from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('register/', include('account.urls')),
    path('channel/', include('channels.urls')),
    path('content/', include('content_viewer.urls')),
    path('push/', include('push.urls')),
    path('api/', include('core_api.urls')),
    path('api/channel/', include('channels_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
