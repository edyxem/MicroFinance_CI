from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from accounts.permissions import IsAdmin
from credits.models import CreditRequest, Installment
from insurance.models import Policy
from chat.models import Conversation
from repayments.models import Payment


class DashboardKPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.now().date()

        credits_par_statut = CreditRequest.objects.values('status').annotate(total=Count('id'))

        total_du = Installment.objects.aggregate(total=Sum('montant_du'))['total'] or 0
        total_paye = Payment.objects.aggregate(total=Sum('montant_recu'))['total'] or 0
        taux_recouvrement = round((float(total_paye) / float(total_du)) * 100, 2) if total_du > 0 else 0

        polices_actives = Policy.objects.filter(status='ACTIVE').count()
        expirations_proches = Policy.objects.filter(
            status='ACTIVE',
            date_fin__lte=today + timedelta(days=30)
        ).count()

        conversations_ouvertes = Conversation.objects.filter(status='OUVERTE').count()
        conversations_en_cours = Conversation.objects.filter(status='EN_COURS').count()

        courbe_credits = []
        for i in range(7, -1, -1):
            debut = today - timedelta(weeks=i+1)
            fin = today - timedelta(weeks=i)
            count = CreditRequest.objects.filter(
                date_soumission__date__gte=debut,
                date_soumission__date__lt=fin
            ).count()
            courbe_credits.append({"semaine": str(debut), "total": count})

        courbe_assurance = []
        for i in range(11, -1, -1):
            mois = today.replace(day=1) - timedelta(days=i*30)
            count = Policy.objects.filter(
                created_at__year=mois.year,
                created_at__month=mois.month
            ).count()
            courbe_assurance.append({"mois": mois.strftime('%Y-%m'), "total": count})

        courbe_support = []
        for i in range(7, -1, -1):
            debut = today - timedelta(weeks=i+1)
            fin = today - timedelta(weeks=i)
            count = Conversation.objects.filter(
                created_at__date__gte=debut,
                created_at__date__lt=fin
            ).count()
            courbe_support.append({"semaine": str(debut), "total": count})

        return Response({
            "credits": {
                "par_statut":       list(credits_par_statut),
                "taux_recouvrement": taux_recouvrement,
                "courbe":           courbe_credits,
            },
            "assurance": {
                "polices_actives":     polices_actives,
                "expirations_proches": expirations_proches,
                "courbe":              courbe_assurance,
            },
            "support": {
                "conversations_ouvertes":  conversations_ouvertes,
                "conversations_en_cours":  conversations_en_cours,
                "courbe":                  courbe_support,
            }
        })