from django.db import models
from accounts.models import User


class InsuranceProduct(models.Model):
    TYPE_CHOICES = [
        ('VIE',   'Assurance vie'),
        ('DECES', 'Décès-invalidité'),
    ]
    nom            = models.CharField(max_length=100)
    type_assurance = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description    = models.TextField()
    duree_mois     = models.IntegerField()
    prix_mensuel   = models.DecimalField(max_digits=10, decimal_places=2)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.type_assurance})"

    class Meta:
        verbose_name = 'Produit d\'assurance'
        verbose_name_plural = 'Produits d\'assurance'


class Policy(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE',   'Active'),
        ('EXPIREE',  'Expirée'),
        ('ANNULEE',  'Annulée'),
    ]
    client               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='policies')
    produit              = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT, related_name='policies')
    beneficiaire_nom     = models.CharField(max_length=150)
    beneficiaire_contact = models.CharField(max_length=20)
    date_debut           = models.DateField()
    date_fin             = models.DateField()
    status               = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Police {self.produit.nom} — {self.client.username} — {self.status}"

    class Meta:
        verbose_name = 'Police d\'assurance'
        verbose_name_plural = 'Polices d\'assurance'
        ordering = ['-created_at']