from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from accounts.services.email_service import EmailService
from accounts.services.email_service import EmailService




User =  get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","full_name","username","email")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField( write_only=True,min_length=8)

    class Meta:
        model = User
        fields = ("full_name","username","email","password")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        EmailService.send_verification_email(user)
        return user

        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email,password=password,)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        try:
            token = RefreshToken(self.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(
                "Invalid or expired refresh token."
            )

class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        uid = attrs.get("uid")
        token = attrs.get("token")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError(
                "Verification link is invalid or has expired."
            )

        attrs["user"] = user
        return attrs