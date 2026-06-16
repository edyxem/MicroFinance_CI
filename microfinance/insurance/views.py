from django.views import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import InsuranceProduct, Policy
from .serializers import InsuranceProductSerializer, PolicySerializer
from accounts.permissions import IsAdmin, IsClient
from notifications.utils import create_notification
from drf_spectacular.utils import extend_schema, OpenApiResponse


class InsuranceProductListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=InsuranceProductSerializer(many=True), tags=["Assurance"])
    def get(self, request):
        produits = InsuranceProduct.objects.filter(is_active=True)
        serializer = InsuranceProductSerializer(produits, many=True)
        return Response(serializer.data)

    @extend_schema(request=InsuranceProductSerializer, responses=InsuranceProductSerializer, tags=["Assurance"])
    def post(self, request):
        if request.user.role != 'ADMIN':
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        serializer = InsuranceProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsuranceProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return InsuranceProduct.objects.get(pk=pk)
        except InsuranceProduct.DoesNotExist:
            return None

    @extend_schema(request=InsuranceProductSerializer, responses=InsuranceProductSerializer, tags=["Assurance"])
    def put(self, request, pk):
        produit = self.get_object(pk)
        if not produit:
            return Response({"error": "Produit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InsuranceProductSerializer(produit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: OpenApiResponse(description="Produit désactivé")}, tags=["Assurance"])
    def delete(self, request, pk):
        produit = self.get_object(pk)
        if not produit:
            return Response({"error": "Produit introuvable."}, status=status.HTTP_404_NOT_FOUND)
        produit.is_active = False
        produit.save()
        return Response({"message": "Produit désactivé."})


class PolicyListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PolicySerializer(many=True), tags=["Assurance"])
    def get(self, request):
        if request.user.role == 'CLIENT':
            policies = Policy.objects.filter(client=request.user)
        else:
            policies = Policy.objects.all()
        serializer = PolicySerializer(policies, many=True)
        return Response(serializer.data)

    @extend_schema(request=PolicySerializer, responses=PolicySerializer, tags=["Assurance"])
    def post(self, request):
        if request.user.role != 'CLIENT':
            return Response({"error": "Seul un client peut souscrire."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PolicySerializer(data=request.data)
        if serializer.is_valid():
            produit = serializer.validated_data['produit']
            date_debut = timezone.now().date()
            date_fin = date_debut + relativedelta(months=produit.duree_mois)
            policy = serializer.save(
                client=request.user,
                date_debut=date_debut,
                date_fin=date_fin
            )
            create_notification(
                destinataires=[request.user],
                type='ASSURANCE',
                titre='Souscription confirmée',
                message=f"Votre souscription à {produit.nom} est confirmée. Validité : {date_debut} → {date_fin}."
            )
            return Response(PolicySerializer(policy).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PolicyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PolicySerializer, tags=["Assurance"])
    def get(self, request, pk):
        try:
            policy = Policy.objects.get(pk=pk)
        except Policy.DoesNotExist:
            return Response({"error": "Police introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'CLIENT' and policy.client != request.user:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        return Response(PolicySerializer(policy).data)

class InsurancePageView(View):
    def get(self, request):
        return render(request, 'client/insurance.html')