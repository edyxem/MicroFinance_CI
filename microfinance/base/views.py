# base/views.py
from django.shortcuts import render
from django.views import View


class HomeView(View):
    """Landing page — redirige vers le dashboard selon le rôle après login."""

    def get(self, request):
        # Si déjà connecté → rediriger vers le bon dashboard
        if request.user.is_authenticated:
            role = getattr(request.user, "role", "CLIENT")
            redirects = {
                "ADMIN":  "/admin-dashboard/",
                "AGENT":  "/agent-dashboard/",
                "CLIENT": "/client-dashboard/",
            }
            from django.shortcuts import redirect
            return redirect(redirects.get(role, "/"))
        return render(request, "common/landing.html")