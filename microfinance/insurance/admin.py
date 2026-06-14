from django.contrib import admin
from insurance.models import InsuranceProduct, Policy
 
 
@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'type_assurance', 'duree_mois', 'prix_mensuel', 'is_active', 'created_at')
    list_filter   = ('type_assurance', 'is_active')
    search_fields = ('nom',)
    list_editable = ('is_active',)
 
 
@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display  = ('id', 'client', 'produit', 'beneficiaire_nom', 'date_debut', 'date_fin', 'status')
    list_filter   = ('status', 'produit__type_assurance')
    search_fields = ('client__username', 'beneficiaire_nom', 'beneficiaire_contact')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)