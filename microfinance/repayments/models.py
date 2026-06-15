from django.db import models
from accounts.models import User
from credits.models import Installment


class Payment(models.Model):
    METHODE_CHOICES = [
        ('CASH',          'Espèces'),
        ('ORANGE_MONEY',  'Orange Money'),
        ('WAVE',          'Wave'),
        ('MTN_MOMO',      'MTN Mobile Money'),
        ('MOOV_MONEY',    'Moov Money'),
    ]
    installment           = models.ForeignKey(Installment, on_delete=models.CASCADE, related_name='payments')
    agent                 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')
    montant_recu          = models.DecimalField(max_digits=12, decimal_places=2)
    date_paiement         = models.DateField()
    methode_paiement      = models.CharField(max_length=20, choices=METHODE_CHOICES, default='CASH')
    numero_mobile_money   = models.CharField(max_length=20, blank=True)
    reference_transaction = models.CharField(max_length=50, blank=True)
    note                  = models.TextField(blank=True)
    created_at            = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.montant_recu} FCFA — Échéance #{self.installment.numero}"

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']