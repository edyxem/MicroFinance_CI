from django.urls import path
from .views import HomeView
from accounts.views import LoginPageView, RegisterPageView, LogoutPageView
from credits.views import ClientDashboardView, AgentDashboardView, AdminDashboardView
from credits.views import CreditFormView, CreditListPageView, CreditDetailPageView
from chat.views import ChatPageView
from insurance.views import InsurancePageView
from notifications.views import NotificationsPageView

urlpatterns = [
    path('',                    HomeView.as_view(),           name='home'),
    path('login/',              LoginPageView.as_view(),      name='login-page'),
    path('register/',           RegisterPageView.as_view(),   name='register-page'),
    path('logout/',             LogoutPageView.as_view(),     name='logout-page'),
    path('client-dashboard/',   ClientDashboardView.as_view(),  name='client-dashboard'),
    path('agent-dashboard/',    AgentDashboardView.as_view(),   name='agent-dashboard'),
    path('admin-dashboard/',    AdminDashboardView.as_view(),   name='admin-dashboard'),
    path('credits/',            CreditListPageView.as_view(),   name='credit-list-page'),
    path('credits/new/',        CreditFormView.as_view(),        name='credit-form'),
    path('credits/<int:pk>/',   CreditDetailPageView.as_view(), name='credit-detail-page'),
    path('chat/',               ChatPageView.as_view(),          name='chat-page'),
    path('chat/<int:pk>/',      ChatPageView.as_view(),          name='chat-room'),
    path('insurance/',          InsurancePageView.as_view(),     name='insurance-page'),
    path('notifications/',      NotificationsPageView.as_view(), name='notifications-page'),
]