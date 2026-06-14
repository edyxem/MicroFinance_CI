from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.utils import timezone


def calculer_score(client):
    score = 0
    credits_passes = client.credit_requests.filter(status='SOLDEE')

    if not credits_passes.exists():
        score += 20
    else:
        retards = 0
        for credit in credits_passes:
            retards += credit.installments.filter(status='EN_RETARD').count()
        if retards == 0:
            score += 40
        elif retards <= 2:
            score += 15
        else:
            score += 0

    anciennete = (timezone.now().date() - client.date_joined.date()).days
    if anciennete > 365:
        score += 30
    elif anciennete > 180:
        score += 20
    else:
        score += 10

    from repayments.models import Payment
    from django.db.models import Sum
    total_paye = Payment.objects.filter(
        installment__credit__client=client
    ).aggregate(total=Sum('montant_recu'))['total'] or 0

    if total_paye > 100000:
        score += 30
    elif total_paye > 0:
        score += 20
    else:
        score += 10

    return score


def generer_echeancier(credit):
    from .models import Installment
    taux = Decimal(str(credit.taux_interet)) / Decimal('100')
    montant = Decimal(str(credit.montant))
    duree = credit.duree_mois

    if taux == 0:
        mensualite = montant / duree
    else:
        mensualite = montant * (taux / (1 - (1 + taux) ** -duree))
        mensualite = mensualite.quantize(Decimal('0.01'))

    date_debut = timezone.now().date()

    for i in range(1, duree + 1):
        date_prevue = date_debut + relativedelta(months=i)
        Installment.objects.create(
            credit=credit,
            numero=i,
            date_prevue=date_prevue,
            montant_du=mensualite,
        )