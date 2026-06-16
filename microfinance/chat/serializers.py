from rest_framework import serializers
from .models import Conversation, Message
from accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    expediteur_detail = UserSerializer(source='expediteur', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'expediteur', 'expediteur_detail',
            'contenu', 'fichier', 'is_auto', 'created_at'
        ]
        read_only_fields = ['id', 'expediteur', 'is_auto', 'created_at']

    def validate(self, data):
        contenu = data.get('contenu', '')
        fichier = data.get('fichier')
        if not contenu and not fichier:
            raise serializers.ValidationError("Le message doit contenir du texte ou un fichier.")
        return data


class ConversationSerializer(serializers.ModelSerializer):
    client_detail = UserSerializer(source='client', read_only=True)
    agent_detail = UserSerializer(source='agent', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    nb_messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'client', 'client_detail',
            'agent', 'agent_detail',
            'status', 'created_at', 'updated_at',
            'messages', 'nb_messages'
        ]
        read_only_fields = ['id', 'client', 'status', 'created_at', 'updated_at']

    def get_nb_messages(self, obj) -> int:
        return obj.messages.count()