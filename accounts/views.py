from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .serializers import LogoutSerializer, VerifyEmailSerializer
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "user": UserSerializer(data["user"]).data,
                    "tokens": data["tokens"],
                },
            }, status=status.HTTP_200_OK
        )

# this will later change into using a profile model.
class ProfileAPIView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())

        return Response(
            {
                "success": True,
                "message": "Profile retrieved successfully.",
                "data": serializer.data,
            }
        )

class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Logged out successfully.",
            }
        )


class VerifyEmailAPIView(GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if user.is_verified:
            return Response(
                {
                    "success": False,
                    "message": "Email has already been verified.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return Response(
            {
                "success": True,
                "message": "Email verified successfully.",
            },
            status=status.HTTP_200_OK,
        )