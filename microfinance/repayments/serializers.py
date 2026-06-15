from rest_framework import serializers
from .models import Payment
from credits.serializers import InstallmentSerializer
from accounts.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    installment_detail = InstallmentSerializer(source='installment', read_only=True)
    agent_detail = UserSerializer(source='agent', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'installment', 'installment_detail',
            'agent', 'agent_detail',
            'montant_recu', 'date_paiement',
            'methode_paiement', 'numero_mobile_money', 'reference_transaction',
            'note', 'created_at'
        ]
        read_only_fields = ['id', 'agent', 'created_at']

    def validate_montant_recu(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant reçu doit être supérieur à 0.")
        return value

    def validate(self, data):
        methode = data.get('methode_paiement', 'CASH')
        if methode != 'CASH' and not data.get('numero_mobile_money'):
            raise serializers.ValidationError(
                {"numero_mobile_money": "Le numéro Mobile Money est obligatoire pour ce moyen de paiement."}
            )
        return data