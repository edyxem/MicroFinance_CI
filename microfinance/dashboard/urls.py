from django.urls import path
from .views import DashboardKPIView

urlpatterns = [
    path('', DashboardKPIView.as_view(), name='dashboard-kpi'),
]