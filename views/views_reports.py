import csv
from io import BytesIO
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils import timezone
from accounts.permissions import IsAdmin
from credits.models import CreditRequest
from repayments.models import Payment
from django.db.models import Sum


class ExportCreditsCSVView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="credits.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Client', 'Montant', 'Durée', 'Statut', 'Date soumission', 'Région'])
        credits = CreditRequest.objects.select_related('client').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            credits = credits.filter(status=status_filter)
        for credit in credits:
            writer.writerow([
                credit.pk,
                credit.client.username,
                credit.montant,
                credit.duree_mois,
                credit.status,
                credit.date_soumission.strftime('%Y-%m-%d'),
                credit.client.region
            ])
        return response


class ExportRapportPDFView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        today = timezone.now().date()
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 800, "COFINANCE CI — Rapport mensuel")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 780, f"Généré le : {today}")

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, 740, "Crédits")
        pdf.setFont("Helvetica", 11)
        total_credits = CreditRequest.objects.count()
        credits_en_cours = CreditRequest.objects.filter(status__in=['APPROUVEE', 'DECAISSEE']).count()
        pdf.drawString(70, 720, f"Total demandes : {total_credits}")
        pdf.drawString(70, 705, f"En cours : {credits_en_cours}")

        total_du = Payment.objects.aggregate(t=Sum('installment__montant_du'))['t'] or 0
        total_paye = Payment.objects.aggregate(t=Sum('montant_recu'))['t'] or 0
        taux = round((float(total_paye) / float(total_du)) * 100, 2) if total_du > 0 else 0
        pdf.drawString(70, 690, f"Taux de recouvrement : {taux}%")

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, 660, "Assurance")
        pdf.setFont("Helvetica", 11)
        from insurance.models import Policy
        polices_actives = Policy.objects.filter(status='ACTIVE').count()
        pdf.drawString(70, 640, f"Polices actives : {polices_actives}")

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, 610, "Support")
        pdf.setFont("Helvetica", 11)
        from chat.models import Conversation
        total_conv = Conversation.objects.count()
        resolues = Conversation.objects.filter(status='RESOLUE').count()
        pdf.drawString(70, 590, f"Total conversations : {total_conv}")
        pdf.drawString(70, 575, f"Résolues : {resolues}")

        pdf.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf',
                            headers={'Content-Disposition': 'attachment; filename="rapport.pdf"'})