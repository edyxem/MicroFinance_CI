from django.db import models
from accounts.models import User


class Conversation(models.Model):
    STATUS_CHOICES = [
        ('OUVERTE',  'Ouverte'),
        ('EN_COURS', 'En cours'),
        ('RESOLUE',  'Résolue'),
    ]
    client     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_client')
    agent      = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='conversations_agent')
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OUVERTE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation #{self.pk} — {self.client.username} — {self.status}"

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    expediteur   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    contenu      = models.TextField(blank=True)
    fichier      = models.FileField(upload_to='chat/fichiers/', blank=True, null=True)
    is_auto      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message #{self.pk} — {self.expediteur.username} — Conv #{self.conversation.pk}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['conversation', 'created_at']