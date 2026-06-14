from rest_framework import serializers
from .models import CreditRequest, Installment
from accounts.serializers import UserSerializer


class InstallmentSerializer(serializers.ModelSerializer):
    reste_a_payer = serializers.SerializerMethodField()

    class Meta:
        model = Installment
        fields = [
            'id', 'numero', 'date_prevue', 'montant_du',
            'montant_paye', 'penalite', 'status', 'reste_a_payer'
        ]
        read_only_fields = ['id']

    def get_reste_a_payer(self, obj):
        return obj.get_reste_a_payer()


class CreditRequestSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    client_detail = UserSerializer(source='client', read_only=True)
    agent_detail = UserSerializer(source='agent', read_only=True)

    class Meta:
        model = CreditRequest
        fields = [
            'id', 'client', 'client_detail', 'agent', 'agent_detail',
            'montant', 'duree_mois', 'taux_interet', 'status',
            'motif_refus', 'score', 'document',
            'date_soumission', 'date_decaissement', 'updated_at',
            'installments'
        ]
        read_only_fields = [
            'id', 'client', 'status', 'score',
            'date_soumission', 'updated_at', 'installments'
        ]


class CreditStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = ['status', 'motif_refus', 'date_decaissement']

    def validate(self, data):
        status = data.get('status')
        motif_refus = data.get('motif_refus')
        if status == 'REFUSEE' and not motif_refus:
            raise serializers.ValidationError({"motif_refus": "Le motif de refus est obligatoire."})
        return data