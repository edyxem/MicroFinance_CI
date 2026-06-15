from django.views import View
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, LoginHistory
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, LoginHistorySerializer
from .permissions import IsAdmin


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# ── Auth ─────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Compte créé avec succès."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if not user:
                return Response(
                    {"error": "Identifiants incorrects."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if not user.is_active:
                return Response(
                    {"error": "Ce compte est désactivé."},
                    status=status.HTTP_403_FORBIDDEN
                )
            refresh = RefreshToken.for_user(user)
            LoginHistory.objects.create(user=user, ip_address=get_client_ip(request))
            return Response({
                "access":  str(refresh.access_token),
                "refresh": str(refresh),
                "user":    UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Déconnexion réussie."})
        except Exception:
            return Response({"error": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST)


# ── Profil ───────────────────────────────────────────────────────────

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = LoginHistory.objects.filter(user=request.user)
        serializer = LoginHistorySerializer(history, many=True)
        return Response(serializer.data)


# ── Gestion utilisateurs (Admin) ─────────────────────────────────────

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all()
        role = request.query_params.get('role')
        if role:
            users = users.filter(role=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if user.credit_requests.filter(status__in=['APPROUVEE', 'DECAISSEE']).exists():
            return Response(
                {"error": "Impossible de supprimer un utilisateur avec un crédit actif."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return Response({"message": "Utilisateur supprimé."}, status=status.HTTP_204_NO_CONTENT)


class UserToggleActiveView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = not user.is_active
        user.save()
        state = "activé" if user.is_active else "désactivé"
        return Response({"message": f"Compte {state} avec succès."})

# ── Pages HTML (pour les clients) ───────────────────────────────────
class LoginPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'common/login.html')

class RegisterPageView(View):
    def get(self, request):
        return render(request, 'common/register.html')

class LogoutPageView(View):
    def get(self, request):
        return render(request, 'common/logout.html')