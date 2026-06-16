from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
from .models import Payment
from .serializers import PaymentSerializer
from credits.models import Installment, CreditRequest
from credits.serializers import InstallmentSerializer
from accounts.permissions import IsAgentOrAdmin
from notifications.utils import create_notification
from drf_spectacular.utils import extend_schema, OpenApiResponse


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAgentOrAdmin]

    @extend_schema(request=PaymentSerializer, responses=PaymentSerializer, tags=["Remboursements"])
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            installment = serializer.validated_data['installment']
            montant_recu = serializer.validated_data['montant_recu']
            date_paiement = serializer.validated_data.get('date_paiement') or timezone.now().date()
            payment = serializer.save(agent=request.user, date_paiement=date_paiement)

            installment.montant_paye = installment.montant_paye + montant_recu
            if installment.montant_paye >= installment.montant_du + installment.penalite:
                installment.status = 'PAYEE'
            installment.save()

            credit = installment.credit
            toutes_payees = not credit.installments.exclude(status='PAYEE').exists()
            if toutes_payees:
                credit.status = 'SOLDEE'
                credit.save()
                create_notification(
                    destinataires=[credit.client],
                    type='REMBOURSEMENT',
                    titre='Crédit soldé',
                    message=f"Félicitations ! Votre crédit #{credit.pk} est entièrement remboursé."
                )

            if payment.methode_paiement != 'CASH':
                message_paiement = (
                    f"Un paiement de {montant_recu} FCFA via {payment.get_methode_paiement_display()} "
                    f"a été enregistré sur votre échéance #{installment.numero} "
                    f"(réf : {payment.reference_transaction or 'N/A'})."
                )
            else:
                message_paiement = f"Un paiement de {montant_recu} FCFA a été enregistré sur votre échéance #{installment.numero}."

            create_notification(
                destinataires=[credit.client],
                type='REMBOURSEMENT',
                titre='Paiement enregistré',
                message=message_paiement
            )
            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PaymentSerializer(many=True), tags=["Remboursements"])
    def get(self, request, credit_pk):
        try:
            credit = CreditRequest.objects.get(pk=credit_pk)
        except CreditRequest.DoesNotExist:
            return Response({"error": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'CLIENT' and credit.client != request.user:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        payments = Payment.objects.filter(installment__credit=credit)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class OverdueCheckView(APIView):
    permission_classes = [IsAuthenticated, IsAgentOrAdmin]

    @extend_schema(request=None,
                   responses={200: OpenApiResponse(description="Échéances en retard mises à jour")},
                   tags=["Remboursements"])
    def post(self, request):
        today = timezone.now().date()
        # On traite uniquement EN_ATTENTE pour éviter de recumuler les pénalités
        overdues = Installment.objects.filter(
            status='EN_ATTENTE',
            date_prevue__lt=today
        )
        count = 0
        for installment in overdues:
            jours_retard = (today - installment.date_prevue).days
            # Pénalité = taux mensuel converti en journalier × jours × capital restant
            taux_journalier = installment.credit.taux_interet / Decimal('100') / Decimal('30')
            penalite = (installment.montant_du - installment.montant_paye) * taux_journalier * jours_retard
            installment.penalite = penalite.quantize(Decimal('0.01'))
            installment.status = 'EN_RETARD'
            installment.save()
            count += 1
            create_notification(
                destinataires=[installment.credit.client],
                type='REMBOURSEMENT',
                titre='Échéance en retard',
                message=f"Votre échéance #{installment.numero} du {installment.date_prevue} est en retard ({jours_retard} jour(s))."
            )
        return Response({"message": f"{count} échéances mises à jour en retard."})