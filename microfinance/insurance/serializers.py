from rest_framework import serializers
from .models import InsuranceProduct, Policy
from accounts.serializers import UserSerializer


class InsuranceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProduct
        fields = [
            'id', 'nom', 'type_assurance', 'description',
            'duree_mois', 'prix_mensuel', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PolicySerializer(serializers.ModelSerializer):
    client_detail = UserSerializer(source='client', read_only=True)
    produit_detail = InsuranceProductSerializer(source='produit', read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id', 'client', 'client_detail',
            'produit', 'produit_detail',
            'beneficiaire_nom', 'beneficiaire_contact',
            'date_debut', 'date_fin', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'client', 'date_debut', 'date_fin', 'status', 'created_at']