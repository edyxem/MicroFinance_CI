from django.db import models
from accounts.models import User


class CreditRequest(models.Model):
    STATUS_CHOICES = [
        ('SOUMISE',     'Soumise'),
        ('EN_ANALYSE',  'En analyse'),
        ('APPROUVEE',   'Approuvée'),
        ('DECAISSEE',   'Décaissée'),
        ('REFUSEE',     'Refusée'),
        ('SOLDEE',      'Soldée'),
    ]
    client             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_requests')
    agent              = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_credits')
    montant            = models.DecimalField(max_digits=12, decimal_places=2)
    duree_mois         = models.IntegerField()
    taux_interet       = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOUMISE')
    motif_refus        = models.TextField(blank=True, null=True)
    score              = models.IntegerField(null=True, blank=True)
    document           = models.FileField(upload_to='credits/documents/', blank=True, null=True)
    date_soumission    = models.DateTimeField(auto_now_add=True)
    date_decaissement  = models.DateField(null=True, blank=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Crédit #{self.pk} — {self.client.username} — {self.status}"

    class Meta:
        verbose_name = 'Demande de crédit'
        verbose_name_plural = 'Demandes de crédit'
        ordering = ['-date_soumission']


class Installment(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('PAYEE',      'Payée'),
        ('EN_RETARD',  'En retard'),
    ]
    credit        = models.ForeignKey(CreditRequest, on_delete=models.CASCADE, related_name='installments')
    numero        = models.IntegerField()
    date_prevue   = models.DateField()
    montant_du    = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    penalite      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')

    def __str__(self):
        return f"Échéance #{self.numero} — Crédit #{self.credit.pk} — {self.status}"

    def get_reste_a_payer(self):
        return self.montant_du + self.penalite - self.montant_paye

    class Meta:
        verbose_name = 'Échéance'
        verbose_name_plural = 'Échéances'
        ordering = ['credit', 'numero']