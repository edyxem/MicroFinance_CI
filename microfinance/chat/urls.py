from django.urls import path
from .views import (
    ConversationListView, ConversationDetailView,
    ConversationAssignView, ConversationCloseView,
    MessageListView, MessageCreateView
)

urlpatterns = [
    # Conversations
    path('',                                        ConversationListView.as_view(),     name='conversation-list'),
    path('<int:pk>/',                               ConversationDetailView.as_view(),   name='conversation-detail'),
    path('<int:pk>/assign/',                        ConversationAssignView.as_view(),   name='conversation-assign'),
    path('<int:pk>/close/',                         ConversationCloseView.as_view(),    name='conversation-close'),

    # Messages
    path('<int:conversation_pk>/messages/',         MessageListView.as_view(),          name='message-list'),
    path('<int:conversation_pk>/messages/send/',    MessageCreateView.as_view(),        name='message-send'),
]