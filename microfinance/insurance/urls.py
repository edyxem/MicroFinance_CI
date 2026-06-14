from django.urls import path
from .views import (
    InsuranceProductListView, InsuranceProductDetailView,
    PolicyListView, PolicyDetailView
)

urlpatterns = [
    # Produits
    path('products/',               InsuranceProductListView.as_view(),     name='product-list'),
    path('products/<int:pk>/',      InsuranceProductDetailView.as_view(),   name='product-detail'),

    # Polices
    path('policies/',               PolicyListView.as_view(),               name='policy-list'),
    path('policies/<int:pk>/',      PolicyDetailView.as_view(),             name='policy-detail'),
]