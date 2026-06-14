from django.contrib import admin
from credits.models import CreditRequest, Installment
 
 
class InstallmentInline(admin.TabularInline):
    model         = Installment
    extra         = 0
    readonly_fields = ('numero', 'date_prevue', 'montant_du', 'montant_paye', 'penalite', 'status')
    can_delete    = False
 
 
@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display  = ('id', 'client', 'agent', 'montant', 'duree_mois', 'taux_interet', 'status', 'score', 'date_soumission')
    list_filter   = ('status', 'taux_interet', 'date_soumission')
    search_fields = ('client__username', 'agent__username')
    ordering      = ('-date_soumission',)
    readonly_fields = ('date_soumission', 'updated_at', 'score')
    inlines       = [InstallmentInline]
    list_editable = ('status',)
 
 
@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'credit', 'numero', 'date_prevue', 'montant_du', 'montant_paye', 'penalite', 'status')
    list_filter   = ('status',)
    search_fields = ('credit__client__username',)
    ordering      = ('credit', 'numero')