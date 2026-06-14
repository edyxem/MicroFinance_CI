from django.db import models
from accounts.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('CREDIT',         'Crédit'),
        ('REMBOURSEMENT',  'Remboursement'),
        ('ASSURANCE',      'Assurance'),
        ('SUPPORT',        'Support / Chat'),
        ('SYSTEME',        'Système'),
    ]
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type         = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre        = models.CharField(max_length=200)
    message      = models.TextField()
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.type}] {self.titre} → {self.destinataire.username}"

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']