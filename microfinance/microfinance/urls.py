from django.urls import path, include
from drf_spectacular.views import SpectacularSchemaView, SpectacularSwaggerView

urlpatterns = [

    # ── Pages HTML ─────────────────────────────────────────
    path('',                include('base.urls')),

    # ── API REST ───────────────────────────────────────────
    path('api/auth/',           include('accounts.urls')),
    path('api/credits/',        include('credits.urls')),
    path('api/repayments/',     include('repayments.urls')),
    path('api/insurance/',      include('insurance.urls')),
    path('api/dashboard/',      include('dashboard.urls')),
    path('api/notifications/',  include('notifications.urls')),
    path('api/chat/',           include('chat.urls')),
    path('api/reports/',        include('reports.urls')),

    # ── Documentation Swagger ──────────────────────────────
    path('api/schema/',     SpectacularSchemaView.as_view(),                    name='schema'),
    path('api/docs/',       SpectacularSwaggerView.as_view(url_name='schema'),  name='swagger-ui'),
]