import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    # ── Cycle de vie ─────────────────────────────────────────────────────────

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"
        self.user = self.scope.get("user")

        # 1. Authentification — injectée par JWTAuthMiddleware
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        # 2. Autorisation — vérifier l'accès à cette conversation
        has_access = await self._check_access()
        if not has_access:
            await self.close(code=4003)
            return

        # 3. Rejoindre le groupe Channels de la conversation
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # 4. Annoncer la présence aux autres membres du groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence",
                "user_id": self.user.id,
                "username": self.user.username,
                "status": "online",
            },
        )

    async def disconnect(self, close_code):
        if not hasattr(self, "room_group_name"):
            return

        # Annoncer la déconnexion
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence",
                "user_id": getattr(self.user, "id", None),
                "username": getattr(self.user, "username", ""),
                "status": "offline",
            },
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Reçoit un message depuis le JS côté client."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("Format JSON invalide.")
            return

        msg_type = data.get("type")

        if msg_type == "chat_message":
            contenu = data.get("contenu", "").strip()
            if not contenu:
                await self._send_error("Le message ne peut pas être vide.")
                return
            message = await self._save_message(contenu)
            if message is None:
                await self._send_error("Conversation introuvable ou déjà résolue.")
                return
            # Broadcaster à tout le groupe (y compris l'émetteur)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": message.id,
                    "contenu": message.contenu,
                    "expediteur_id": self.user.id,
                    "expediteur_username": self.user.username,
                    "expediteur_role": self.user.role,
                    "created_at": message.created_at.isoformat(),
                },
            )

        elif msg_type == "typing":
            # Indicateur de frappe — PAS sauvegardé en DB
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "is_typing": bool(data.get("is_typing", False)),
                },
            )

        else:
            await self._send_error(f"Type de message inconnu : {msg_type}")

    # ── Handlers de groupe (appelés par group_send) ──────────────────────────

    async def chat_message(self, event):
        """Pousse un message texte vers le client WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message_id": event["message_id"],
            "contenu": event["contenu"],
            "expediteur_id": event["expediteur_id"],
            "expediteur_username": event["expediteur_username"],
            "expediteur_role": event["expediteur_role"],
            "created_at": event["created_at"],
        }))

    async def typing(self, event):
        """Pousse l'indicateur de frappe — seulement aux AUTRES membres."""
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "typing",
                "user_id": event["user_id"],
                "username": event["username"],
                "is_typing": event["is_typing"],
            }))

    async def presence(self, event):
        """Pousse l'événement de présence (online/offline) aux AUTRES membres."""
        if event["user_id"] != getattr(self.user, "id", None):
            await self.send(text_data=json.dumps({
                "type": "presence",
                "user_id": event["user_id"],
                "username": event["username"],
                "status": event["status"],
            }))

    # ── Helpers DB ────────────────────────────────────────────────────────────

    @database_sync_to_async
    def _check_access(self):
        try:
            conv = Conversation.objects.get(pk=self.conversation_id)
            if conv.status == "RESOLUE":
                return False
            if self.user.role == "CLIENT":
                return conv.client_id == self.user.id
            return True  # AGENT et ADMIN ont accès à toutes
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_message(self, contenu):
        try:
            from notifications.utils import create_notification
            conv = Conversation.objects.get(pk=self.conversation_id)
            if conv.status == "RESOLUE":
                return None
            # Un agent qui répond → conversation passe EN_COURS
            if conv.status == "OUVERTE" and self.user.role in ("AGENT", "ADMIN"):
                conv.status = "EN_COURS"
                conv.save(update_fields=["status", "updated_at"])

            message = Message.objects.create(
                conversation=conv,
                expediteur=self.user,
                contenu=contenu,
            )

            # ── Notification au destinataire ──────────────────────────────
            extrait = contenu[:60] + ("…" if len(contenu) > 60 else "")
            if self.user.role == "CLIENT":
                # Client → notifier l'agent assigné (ou tous les agents si non assigné)
                if conv.agent:
                    destinataires = [conv.agent]
                else:
                    from accounts.models import User
                    destinataires = list(User.objects.filter(role="AGENT", is_active=True))
                create_notification(
                    destinataires=destinataires,
                    type="SUPPORT",
                    titre=f"Nouveau message de {self.user.username}",
                    message=f"Conv #{conv.id} : « {extrait} »",
                )
            else:
                # Agent/Admin → notifier le client
                create_notification(
                    destinataires=[conv.client],
                    type="SUPPORT",
                    titre=f"Réponse de {self.user.username}",
                    message=f"« {extrait} »",
                )

            return message

        except Conversation.DoesNotExist:
            return None

    async def _send_error(self, detail):
        await self.send(text_data=json.dumps({"type": "error", "detail": detail}))