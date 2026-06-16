from django.views import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer
from rest_framework import serializers as drf_serializers


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[OpenApiParameter("type", str, description="Filtre par type")],
                   responses=NotificationSerializer(many=True), tags=["Notifications"])
    def get(self, request):
        notifications = Notification.objects.filter(destinataire=request.user)
        type_filter = request.query_params.get('type')
        if type_filter:
            notifications = notifications.filter(type=type_filter)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Marquée comme lue")}, tags=["Notifications"])
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, destinataire=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marquée comme lue."})


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: OpenApiResponse(description="Toutes marquées lues")}, tags=["Notifications"])
    def post(self, request):
        Notification.objects.filter(
            destinataire=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({"message": "Toutes les notifications marquées comme lues."})


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=inline_serializer("UnreadCount", {"unread_count": drf_serializers.IntegerField()}), tags=["Notifications"])
    def get(self, request):
        count = Notification.objects.filter(
            destinataire=request.user,
            is_read=False
        ).count()
        return Response({"unread_count": count})

class NotificationsPageView(View):
    def get(self, request):
        return render(request, 'client/notifications.html')