from django.urls import path
from .views import HomeView, template_view

urlpatterns = [

    # ── Pages communes ────────────────────────────────────
    path('',            HomeView.as_view(),                         name='home'),
    path('login/',      template_view('common/login.html'),         name='login'),
    path('register/',   template_view('common/register.html'),      name='register'),

    # ── Espace client ─────────────────────────────────────
    path('client-dashboard/',           template_view('client/dashboard.html'),             name='client-dashboard'),
    path('client/credits/',             template_view('client/credit_list.html'),           name='client-credit-list'),
    path('client/credits/new/',         template_view('client/credit_form.html'),           name='client-credit-new'),
    path('client/credits/<int:pk>/',    template_view('client/credit_detail.html'),         name='client-credit-detail'),
    path('client/repayments/',          template_view('client/repayments.html'),            name='client-repayments'),
    path('client/insurance/',           template_view('client/insurance_list.html'),        name='client-insurance'),
    path('client/insurance/subscribe/', template_view('client/insurance_subscribe.html'),   name='client-insurance-subscribe'),
    path('client/chat/',                template_view('client/chat.html'),                  name='client-chat'),
    path('client/notifications/',       template_view('client/notifications.html'),         name='client-notifications'),
    path('client/profile/',             template_view('client/profile.html'),               name='client-profile'),

    # ── Espace agent ──────────────────────────────────────
    path('agent-dashboard/',                    template_view('agent/dashboard.html'),          name='agent-dashboard'),
    path('agent/credits/',                      template_view('agent/credit_list.html'),        name='agent-credit-list'),
    path('agent/credits/<int:pk>/',             template_view('agent/credit_detail.html'),      name='agent-credit-detail'),
    path('agent/payments/',                     template_view('agent/payment_form.html'),       name='agent-payment-form'),
    path('agent/conversations/',                template_view('agent/conversations.html'),      name='agent-conversations'),
    path('agent/conversations/<int:pk>/',       template_view('agent/chat_detail.html'),        name='agent-chat-detail'),

    # ── Espace admin ──────────────────────────────────────
    path('admin-dashboard/',        template_view('admin/dashboard.html'),          name='admin-dashboard'),
    path('admin/credits/',          template_view('admin/credit_list.html'),        name='admin-credit-list'),
    path('admin/credits/<int:pk>/', template_view('admin/credit_detail.html'),      name='admin-credit-detail'),
    path('admin/users/',            template_view('admin/users.html'),              name='admin-users'),
    path('admin/insurance/',        template_view('admin/insurance_catalog.html'),  name='admin-insurance'),
    path('admin/reports/',          template_view('admin/reports.html'),            name='admin-reports'),
]