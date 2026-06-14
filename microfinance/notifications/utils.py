from .models import Notification
from accounts.models import User


def create_notification(type, titre, message, destinataires=None, destinataires_role=None):
    users = []
    if destinataires:
        users = list(destinataires)
    if destinataires_role:
        users += list(User.objects.filter(role__in=destinataires_role))
    for user in set(users):
        Notification.objects.create(
            destinataire=user,
            type=type,
            titre=titre,
            message=message
        )