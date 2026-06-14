from django.contrib import admin
from repayments.models import Payment
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'installment', 'agent', 'montant_recu', 'date_paiement', 'created_at')
    list_filter   = ('date_paiement', 'agent')
    search_fields = ('installment__credit__client__username', 'agent__username')
    ordering      = ('-date_paiement',)
    readonly_fields = ('created_at',)