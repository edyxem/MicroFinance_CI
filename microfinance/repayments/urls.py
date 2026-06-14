from django.urls import path
from .views import (
    PaymentCreateView, PaymentHistoryView, OverdueCheckView
)

urlpatterns = [
    path('',                            PaymentCreateView.as_view(),    name='payment-create'),
    path('credits/<int:credit_pk>/',    PaymentHistoryView.as_view(),   name='payment-history'),
    path('check-overdue/',              OverdueCheckView.as_view(),     name='check-overdue'),
]