from django.urls import path, include
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',                include('base.urls')),
    path('api/auth/',           include('accounts.urls')),
    path('api/credits/',        include('credits.urls')),
    path('api/repayments/',     include('repayments.urls')),
    path('api/insurance/',      include('insurance.urls')),
    path('api/dashboard/',      include('dashboard.urls')),
    path('api/notifications/',  include('notifications.urls')),
    path('api/chat/',           include('chat.urls')),
    path('api/reports/',        include('reports.urls')),
    path('api/schema/',     SpectacularAPIView.as_view(),                      name='schema'),
    path('api/docs/',       SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)