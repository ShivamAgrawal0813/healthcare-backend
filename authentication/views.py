from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/ - Register a new user with name, email, and password.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        user_data = UserSerializer(user).data

        headers = self.get_success_headers(serializer.data)
        response_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "access": access_token,
            "refresh": refresh_token,
            "tokens": {
                "access": access_token,
                "refresh": refresh_token,
            },
            "user": user_data,
            "message": "User registered successfully."
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(generics.GenericAPIView):
    """
    POST /api/auth/login/ - Log in a user and return a JWT token.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    """
    GET /api/auth/me/ - Get current authenticated user profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
