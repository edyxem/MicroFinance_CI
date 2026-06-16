"""
Tâche planifiée quotidienne (remplace Celery comme prévu par la roadmap).

À lancer chaque jour, par ex. via cron :
    0 6 * * *  /chemin/venv/bin/python manage.py run_daily_tasks

Couvre les déclencheurs exigés par le cahier des charges :
  - Échéance J-3  : notification CLIENT + AGENT (« votre échéance approche »)
  - Échéance J+1  : passage EN_RETARD + calcul de la pénalité + notification CLIENT + AGENT
  - Assurance J-15 : notification CLIENT (« expire dans 15 jours »)
  - Police expirée : passage EXPIREE + notification CLIENT
"""
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from credits.models import Installment
from insurance.models import Policy
from notifications.utils import create_notification


class Command(BaseCommand):
    help = "Exécute les tâches planifiées quotidiennes (alertes échéances + expirations assurance)."

    def handle(self, *args, **options):
        today = timezone.now().date()
        stats = {"j3": 0, "retard": 0, "assurance_j15": 0, "assurance_expiree": 0}

        # ── 1. Échéances à J-3 ────────────────────────────────────────────
        cible_j3 = today + timedelta(days=3)
        for inst in Installment.objects.filter(status='EN_ATTENTE', date_prevue=cible_j3).select_related('credit__client', 'credit__agent'):
            destinataires = [inst.credit.client]
            if inst.credit.agent:
                destinataires.append(inst.credit.agent)
            create_notification(
                destinataires=destinataires,
                type='REMBOURSEMENT',
                titre='Échéance dans 3 jours',
                message=f"Votre échéance #{inst.numero} (crédit #{inst.credit.pk}) "
                        f"de {inst.montant_du} FCFA est prévue le {inst.date_prevue}.",
            )
            stats["j3"] += 1

        # ── 2. Échéances en retard (J+1 et au-delà) ──────────────────────
        for inst in Installment.objects.filter(status='EN_ATTENTE', date_prevue__lt=today).select_related('credit__client', 'credit__agent'):
            jours_retard = (today - inst.date_prevue).days
            taux_journalier = inst.credit.taux_interet / Decimal('100') / Decimal('30')
            penalite = (inst.montant_du - inst.montant_paye) * taux_journalier * jours_retard
            inst.penalite = penalite.quantize(Decimal('0.01'))
            inst.status = 'EN_RETARD'
            inst.save(update_fields=['penalite', 'status'])

            destinataires = [inst.credit.client]
            if inst.credit.agent:
                destinataires.append(inst.credit.agent)
            create_notification(
                destinataires=destinataires,
                type='REMBOURSEMENT',
                titre='Échéance en retard',
                message=f"Votre échéance #{inst.numero} du {inst.date_prevue} est en retard "
                        f"de {jours_retard} jour(s). Pénalité : {inst.penalite} FCFA.",
            )
            stats["retard"] += 1

        # ── 3. Assurance : expiration dans 15 jours ──────────────────────
        cible_j15 = today + timedelta(days=15)
        for policy in Policy.objects.filter(status='ACTIVE', date_fin=cible_j15).select_related('client', 'produit'):
            create_notification(
                destinataires=[policy.client],
                type='ASSURANCE',
                titre='Votre assurance expire bientôt',
                message=f"Votre police {policy.produit.nom} expire le {policy.date_fin} "
                        f"(dans 15 jours). Pensez à la renouveler.",
            )
            stats["assurance_j15"] += 1

        # ── 4. Assurance : polices expirées ──────────────────────────────
        for policy in Policy.objects.filter(status='ACTIVE', date_fin__lt=today).select_related('client', 'produit'):
            policy.status = 'EXPIREE'
            policy.save(update_fields=['status'])
            create_notification(
                destinataires=[policy.client],
                type='ASSURANCE',
                titre='Assurance expirée',
                message=f"Votre police {policy.produit.nom} a expiré le {policy.date_fin}.",
            )
            stats["assurance_expiree"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Tâches quotidiennes terminées — "
            f"J-3: {stats['j3']}, retards: {stats['retard']}, "
            f"assurance J-15: {stats['assurance_j15']}, "
            f"assurance expirée: {stats['assurance_expiree']}."
        ))
