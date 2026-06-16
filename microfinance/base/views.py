from django.shortcuts import render, redirect
from django.views import View


def template_view(template):
    """Raccourci : retourne une view qui rend un template.
    Accepte les kwargs d'URL (ex: pk) même si le template n'en a pas besoin.
    La protection auth est gérée côté JS par api.js (token JWT dans localStorage).
    """
    def view(request, **kwargs):
        return render(request, template)
    return view


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            role = getattr(request.user, 'role', 'CLIENT')
            redirects = {
                'ADMIN':  '/admin-dashboard/',
                'AGENT':  '/agent-dashboard/',
                'CLIENT': '/client-dashboard/',
            }
            return redirect(redirects.get(role, '/'))
        return render(request, 'common/landing.html')