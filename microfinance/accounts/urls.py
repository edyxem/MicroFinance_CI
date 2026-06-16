from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView,
    ProfileView, LoginHistoryView,
    UserListView, UserDetailView, UserToggleActiveView
)

urlpatterns = [
    # Auth
    path('register/',           RegisterView.as_view(),         name='register'),
    path('login/',              LoginView.as_view(),            name='login'),
    path('logout/',             LogoutView.as_view(),           name='logout'),
    path('refresh/',            TokenRefreshView.as_view(),     name='token-refresh'),

    # Profil
    path('profile/',            ProfileView.as_view(),          name='profile'),
    path('profile/history/',    LoginHistoryView.as_view(),     name='login-history'),

    # Gestion utilisateurs (Admin)
    path('users/',              UserListView.as_view(),         name='user-list'),
    path('users/<int:pk>/',     UserDetailView.as_view(),       name='user-detail'),
    path('users/<int:pk>/toggle/', UserToggleActiveView.as_view(), name='user-toggle'),
]