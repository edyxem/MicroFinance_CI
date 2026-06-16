"""
Exports — COFINANCE·CI
======================
- CSV : liste des crédits (UTF-8 BOM + séparateur ';' pour Excel FR).
- PDF : rapport mensuel restylé à la charte graphique du site
        (bandeau encre sombre + émeraude, cartes KPI, pastilles de statut).
        Polices STANDARD (Helvetica) — aucune police embarquée requise.
"""
import csv
from io import BytesIO

from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas

from accounts.permissions import IsAdmin
from credits.models import CreditRequest, Installment
from repayments.models import Payment
from insurance.models import Policy
from chat.models import Conversation


# ─────────────────────────────────────────────────────────────
#  CHARTE GRAPHIQUE (reprise de cofi.css)
# ─────────────────────────────────────────────────────────────
INK        = HexColor("#0d1411")   # encre sombre
INK2       = HexColor("#13201a")
ACCENT     = HexColor("#0f7a52")   # émeraude
ACCENT_GLW = HexColor("#34c48a")
GOLD       = HexColor("#c08a2d")
PAPER      = HexColor("#f6f3eb")   # fond carte chaud
LINE       = HexColor("#e2ddd1")
MUTED      = HexColor("#8b938d")
INK_SOFT   = HexColor("#42514a")

# pastilles de statut : (fond, texte, libellé)
STATUS = {
    "SOUMISE":   (HexColor("#eef0ee"), HexColor("#6b7280"), "Soumise"),
    "EN_ANALYSE":(HexColor("#fbf1e1"), HexColor("#a4670c"), "En analyse"),
    "APPROUVEE": (HexColor("#e6f2ea"), HexColor("#0f7a52"), "Approuvée"),
    "DECAISSEE": (HexColor("#e7f0f9"), HexColor("#1565a8"), "Décaissée"),
    "SOLDEE":    (HexColor("#e6e6e3"), HexColor("#0d1411"), "Soldée"),
    "REFUSEE":   (HexColor("#fbeae7"), HexColor("#bb3a2c"), "Refusée"),
}

PAGE_W, PAGE_H = A4


# ─────────────────────────────────────────────────────────────
#  Primitives de dessin
# ─────────────────────────────────────────────────────────────
def _pill(pdf, x, y, label, bg, fg, pad=8, size=9):
    pdf.setFont("Helvetica-Bold", size)
    w = pdf.stringWidth(label, "Helvetica-Bold", size) + pad * 2
    pdf.setFillColor(bg)
    pdf.roundRect(x, y, w, size + 8, (size + 8) / 2, fill=1, stroke=0)
    pdf.setFillColor(fg)
    pdf.drawString(x + pad, y + 5, label)
    return w


def _kpi_card(pdf, x, y, w, h, label, value, accent=ACCENT, sub=None):
    pdf.setFillColor(PAPER)
    pdf.roundRect(x, y, w, h, 12, fill=1, stroke=0)
    pdf.setStrokeColor(LINE); pdf.setLineWidth(0.8)
    pdf.roundRect(x, y, w, h, 12, fill=0, stroke=1)
    # accent à gauche
    pdf.setFillColor(accent)
    pdf.roundRect(x, y + 10, 4, h - 20, 2, fill=1, stroke=0)
    pdf.setFillColor(MUTED); pdf.setFont("Helvetica", 8.5)
    pdf.drawString(x + 16, y + h - 20, label.upper())
    pdf.setFillColor(INK); pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(x + 16, y + h - 46, str(value))
    if sub:
        pdf.setFillColor(accent); pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(x + 16, y + 12, sub)


def _section(pdf, x, y, title, eyebrow=None):
    if eyebrow:
        pdf.setFillColor(ACCENT); pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(x, y + 16, eyebrow.upper())
    pdf.setFillColor(INK); pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, title)
    # petit trait émeraude
    pdf.setStrokeColor(ACCENT_GLW); pdf.setLineWidth(2)
    pdf.line(x, y - 7, x + 34, y - 7)


def _header(pdf, today):
    # bandeau encre sombre
    pdf.setFillColor(INK)
    pdf.rect(0, PAGE_H - 130, PAGE_W, 130, fill=1, stroke=0)
    # logo carré émeraude
    pdf.setFillColor(ACCENT)
    pdf.roundRect(45, PAGE_H - 92, 46, 46, 12, fill=1, stroke=0)
    pdf.setFillColor(white); pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(68, PAGE_H - 78, "C")
    # titre
    pdf.setFillColor(white); pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(104, PAGE_H - 66, "COFINANCE")
    pdf.setFillColor(ACCENT_GLW)
    pdf.drawString(104 + pdf.stringWidth("COFINANCE", "Helvetica-Bold", 20), PAGE_H - 66, "·CI")
    pdf.setFillColor(HexColor("#9fb0a7")); pdf.setFont("Helvetica", 8.5)
    pdf.drawString(105, PAGE_H - 80, "MICROFINANCE & ASSURANCE")
    # bloc droit
    pdf.setFillColor(ACCENT_GLW); pdf.setFont("Helvetica-Bold", 13)
    pdf.drawRightString(PAGE_W - 45, PAGE_H - 60, "Rapport mensuel")
    pdf.setFillColor(HexColor("#9fb0a7")); pdf.setFont("Helvetica", 9)
    pdf.drawRightString(PAGE_W - 45, PAGE_H - 78, "Généré le %s" % today.strftime("%d/%m/%Y"))


def _footer(pdf, today):
    pdf.setStrokeColor(LINE); pdf.setLineWidth(0.8)
    pdf.line(45, 54, PAGE_W - 45, 54)
    pdf.setFillColor(MUTED); pdf.setFont("Helvetica", 8)
    pdf.drawString(45, 40, "Document confidentiel · COFINANCE·CI · usage interne")
    pdf.drawRightString(PAGE_W - 45, 40, "Édité le %s à %s" % (today.strftime("%d/%m/%Y"), timezone.now().strftime("%H:%M")))


# ─────────────────────────────────────────────────────────────
#  EXPORT CSV
# ─────────────────────────────────────────────────────────────
class ExportCreditsCSVView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(parameters=[OpenApiParameter("status", str)],
                   responses={200: OpenApiResponse(description="Fichier CSV des crédits")}, tags=["Rapports"])
    def get(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="credits.csv"'
        response.write("\ufeff")  # BOM Excel
        writer = csv.writer(response, delimiter=";")
        writer.writerow(["ID", "Client", "Montant (FCFA)", "Durée (mois)", "Taux %",
                         "Statut", "Score", "Date soumission", "Région", "Agent"])
        credits = CreditRequest.objects.select_related("client", "agent").all()
        status_filter = request.query_params.get("status")
        if status_filter:
            credits = credits.filter(status=status_filter)
        for c in credits:
            writer.writerow([
                c.pk, c.client.username, c.montant, c.duree_mois, c.taux_interet,
                STATUS.get(c.status, (None, None, c.status))[2], c.score,
                c.date_soumission.strftime("%Y-%m-%d"),
                c.client.region or "—",
                c.agent.username if c.agent else "—",
            ])
        return response


# ─────────────────────────────────────────────────────────────
#  EXPORT PDF — rapport mensuel
# ─────────────────────────────────────────────────────────────
class ExportRapportPDFView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(responses={200: OpenApiResponse(description="Rapport mensuel PDF")}, tags=["Rapports"])
    def get(self, request):
        today = timezone.now().date()
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setTitle("COFINANCE·CI — Rapport mensuel")

        # ---- agrégats ----
        total_credits   = CreditRequest.objects.count()
        en_cours        = CreditRequest.objects.filter(status__in=["APPROUVEE", "DECAISSEE"]).count()
        decaisses       = CreditRequest.objects.filter(status="DECAISSEE").count()
        total_du   = Installment.objects.aggregate(t=Sum("montant_du"))["t"] or 0
        total_paye = Payment.objects.aggregate(t=Sum("montant_recu"))["t"] or 0
        taux = round((float(total_paye) / float(total_du)) * 100, 1) if total_du > 0 else 0.0
        par_statut = {r["status"]: r["total"]
                      for r in CreditRequest.objects.values("status").annotate(total=Count("id"))}
        polices_actives = Policy.objects.filter(status="ACTIVE").count()
        polices_total   = Policy.objects.count()
        total_conv = Conversation.objects.count()
        resolues   = Conversation.objects.filter(status="RESOLUE").count()
        ouvertes   = Conversation.objects.filter(status="OUVERTE").count()

        # ---- mise en page ----
        _header(pdf, today)
        M = 45
        y = PAGE_H - 130 - 38

        # Section crédits
        _section(pdf, M, y, "Crédits", eyebrow="Activité de prêt")
        y -= 24
        cw = (PAGE_W - 2 * M - 3 * 12) / 4
        _kpi_card(pdf, M,                 y - 78, cw, 78, "Total demandes", total_credits)
        _kpi_card(pdf, M + (cw + 12),     y - 78, cw, 78, "En cours", en_cours, accent=HexColor("#1565a8"))
        _kpi_card(pdf, M + 2 * (cw + 12), y - 78, cw, 78, "Décaissés", decaisses, accent=ACCENT_GLW)
        _kpi_card(pdf, M + 3 * (cw + 12), y - 78, cw, 78, "Recouvrement", "%s%%" % taux, accent=GOLD,
                  sub="%s k / %s k FCFA" % (round(float(total_paye) / 1000), round(float(total_du) / 1000)))
        y -= 78 + 30

        # Répartition par statut
        _section(pdf, M, y, "Répartition par statut")
        y -= 22
        maxv = max([1] + list(par_statut.values()))
        bar_x = M + 150
        bar_w = PAGE_W - M - bar_x - 60
        for code in ["SOUMISE", "EN_ANALYSE", "APPROUVEE", "DECAISSEE", "SOLDEE", "REFUSEE"]:
            count = par_statut.get(code, 0)
            bg, fg, label = STATUS[code]
            _pill(pdf, M, y - 4, label, bg, fg)
            # barre proportionnelle
            pdf.setFillColor(PAPER)
            pdf.roundRect(bar_x, y - 2, bar_w, 11, 5, fill=1, stroke=0)
            w = (count / maxv) * bar_w
            if w > 0:
                pdf.setFillColor(fg)
                pdf.roundRect(bar_x, y - 2, max(w, 6), 11, 5, fill=1, stroke=0)
            pdf.setFillColor(INK); pdf.setFont("Helvetica-Bold", 11)
            pdf.drawRightString(PAGE_W - M, y, str(count))
            y -= 26
        y -= 14

        # Assurance + Support sur deux colonnes
        col_w = (PAGE_W - 2 * M - 18) / 2
        _section(pdf, M, y, "Assurance", eyebrow="Couverture")
        _section(pdf, M + col_w + 18, y, "Support", eyebrow="Relation client")
        y -= 24
        _kpi_card(pdf, M, y - 70, (col_w - 12) / 2, 70, "Polices actives", polices_actives, accent=ACCENT)
        _kpi_card(pdf, M + (col_w - 12) / 2 + 12, y - 70, (col_w - 12) / 2, 70, "Total polices", polices_total, accent=MUTED)
        _kpi_card(pdf, M + col_w + 18, y - 70, (col_w - 12) / 2, 70, "Conversations", total_conv, accent=HexColor("#1565a8"))
        _kpi_card(pdf, M + col_w + 18 + (col_w - 12) / 2 + 12, y - 70, (col_w - 12) / 2, 70, "Résolues",
                  resolues, accent=ACCENT_GLW, sub="%s ouvertes" % ouvertes)

        _footer(pdf, today)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf",
                            headers={"Content-Disposition": 'attachment; filename="rapport.pdf"'})