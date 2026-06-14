from django.urls import path
from .views import (
    CreditListView, CreditDetailView,
    CreditStatusView, InstallmentListView
)

urlpatterns = [
    # Crédits
    path('',                            CreditListView.as_view(),       name='credit-list'),
    path('<int:pk>/',                   CreditDetailView.as_view(),     name='credit-detail'),
    path('<int:pk>/status/',            CreditStatusView.as_view(),     name='credit-status'),

    # Échéances
    path('<int:credit_pk>/installments/', InstallmentListView.as_view(), name='installment-list'),
]