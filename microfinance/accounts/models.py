from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('AGENT', 'Agent de terrain'),
        ('ADMIN', 'Administrateur'),
    ]
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    phone      = models.CharField(max_length=20, blank=True)
    region     = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'


class LoginHistory(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    logged_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.logged_at}"

    class Meta:
        verbose_name = 'Historique de connexion'
        verbose_name_plural = 'Historiques de connexion'
        ordering = ['-logged_at']