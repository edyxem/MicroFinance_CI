from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import CreditRequest, Installment
from .serializers import CreditRequestSerializer, CreditStatusSerializer, InstallmentSerializer
from .utils import calculer_score, generer_echeancier
from accounts.permissions import IsClient, IsAgentOrAdmin
from notifications.utils import create_notification


class CreditListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'CLIENT':
            credits = CreditRequest.objects.filter(client=request.user)
        else:
            credits = CreditRequest.objects.all()
            status_filter = request.query_params.get('status')
            if status_filter:
                credits = credits.filter(status=status_filter)
        serializer = CreditRequestSerializer(credits, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'CLIENT':
            return Response(
                {"error": "Seul un client peut soumettre une demande."},
                status=status.HTTP_403_FORBIDDEN
            )
        credit_actif = CreditRequest.objects.filter(
            client=request.user,
            status__in=['APPROUVEE', 'DECAISSEE']
        ).exists()
        if credit_actif:
            return Response(
                {"error": "Vous avez déjà un crédit actif en cours."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CreditRequestSerializer(data=request.data)
        if serializer.is_valid():
            credit = serializer.save(client=request.user)
            create_notification(
                destinataires_role=['AGENT', 'ADMIN'],
                type='CREDIT',
                titre='Nouvelle demande de crédit',
                message=f"{request.user.username} a soumis une demande de {credit.montant} FCFA."
            )
            return Response(CreditRequestSerializer(credit).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreditDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            credit = CreditRequest.objects.get(pk=pk)
            if user.role == 'CLIENT' and credit.client != user:
                return None
            return credit
        except CreditRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        credit = self.get_object(pk, request.user)
        if not credit:
            return Response({"error": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CreditRequestSerializer(credit).data)


class CreditStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAgentOrAdmin]

    def post(self, request, pk):
        try:
            credit = CreditRequest.objects.get(pk=pk)
        except CreditRequest.DoesNotExist:
            return Response({"error": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)

        nouveau_status = request.data.get('status')
        transitions_valides = {
            'SOUMISE':    ['EN_ANALYSE'],
            'EN_ANALYSE': ['APPROUVEE', 'REFUSEE'],
            'APPROUVEE':  ['DECAISSEE'],
        }

        if nouveau_status not in transitions_valides.get(credit.status, []):
            return Response(
                {"error": f"Transition invalide : {credit.status} → {nouveau_status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreditStatusSerializer(credit, data=request.data, partial=True)
        if serializer.is_valid():
            if nouveau_status == 'EN_ANALYSE':
                serializer.save(status=nouveau_status, agent=request.user)
                score = calculer_score(credit.client)
                credit.score = score
                credit.save()

            elif nouveau_status == 'APPROUVEE':
                serializer.save(status=nouveau_status)
                generer_echeancier(credit)

            elif nouveau_status == 'DECAISSEE':
                serializer.save(status=nouveau_status, date_decaissement=timezone.now().date())

            elif nouveau_status == 'REFUSEE':
                serializer.save(status=nouveau_status)

            create_notification(
                destinataires=[credit.client],
                type='CREDIT',
                titre=f"Votre crédit est {nouveau_status.lower()}",
                message=f"Le statut de votre demande #{credit.pk} est passé à {nouveau_status}."
            )
            return Response(CreditRequestSerializer(credit).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstallmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, credit_pk):
        try:
            credit = CreditRequest.objects.get(pk=credit_pk)
        except CreditRequest.DoesNotExist:
            return Response({"error": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'CLIENT' and credit.client != request.user:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        installments = credit.installments.all()
        serializer = InstallmentSerializer(installments, many=True)
        return Response(serializer.data)