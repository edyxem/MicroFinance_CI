from django.views import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from accounts.permissions import IsAgentOrAdmin, IsClient
from notifications.utils import create_notification


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'CLIENT':
            conversations = Conversation.objects.filter(client=request.user)
        else:
            conversations = Conversation.objects.all()
            status_filter = request.query_params.get('status')
            if status_filter:
                conversations = conversations.filter(status=status_filter)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'CLIENT':
            return Response(
                {"error": "Seul un client peut ouvrir une conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        conversation = Conversation.objects.create(client=request.user)
        Message.objects.create(
            conversation=conversation,
            expediteur=request.user,
            contenu=f"Bonjour {request.user.username}, un agent va vous répondre sous peu.",
            is_auto=True
        )
        create_notification(
            destinataires_role=['AGENT', 'ADMIN'],
            type='SUPPORT',
            titre='Nouvelle conversation support',
            message=f"{request.user.username} a ouvert une conversation de support."
        )
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            conversation = Conversation.objects.get(pk=pk)
            if user.role == 'CLIENT' and conversation.client != user:
                return None
            return conversation
        except Conversation.DoesNotExist:
            return None

    def get(self, request, pk):
        conversation = self.get_object(pk, request.user)
        if not conversation:
            return Response({"error": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ConversationSerializer(conversation).data)


class ConversationAssignView(APIView):
    permission_classes = [IsAuthenticated, IsAgentOrAdmin]

    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        conversation.agent = request.user
        conversation.status = 'EN_COURS'
        conversation.save()
        return Response(ConversationSerializer(conversation).data)


class ConversationCloseView(APIView):
    permission_classes = [IsAuthenticated, IsAgentOrAdmin]

    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        conversation.status = 'RESOLUE'
        conversation.save()
        create_notification(
            destinataires=[conversation.client],
            type='SUPPORT',
            titre='Conversation résolue',
            message="Votre demande de support a été résolue."
        )
        return Response({"message": "Conversation clôturée."})


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_pk):
        try:
            conversation = Conversation.objects.get(pk=conversation_pk)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'CLIENT' and conversation.client != request.user:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_pk):
        try:
            conversation = Conversation.objects.get(pk=conversation_pk)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'CLIENT' and conversation.client != request.user:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                conversation=conversation,
                expediteur=request.user
            )
            if request.user.role == 'CLIENT' and conversation.agent:
                destinataire = conversation.agent
            elif request.user.role in ['AGENT', 'ADMIN']:
                destinataire = conversation.client
            else:
                destinataire = None
            if destinataire:
                create_notification(
                    destinataires=[destinataire],
                    type='SUPPORT',
                    titre='Nouveau message',
                    message=f"{request.user.username} vous a envoyé un message."
                )
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatPageView(View):
    def get(self, request, pk=None):
        return render(request, 'client/chat.html', {'conversation_id': pk})