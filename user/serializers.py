from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "is_superuser",
            "is_active",
            "password",
            "email",
            "date_joined",
        ]

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        # You can add additional validation logic here if needed

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if the provided email exists in the User model snsnj
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found with this email.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        new_password = data.get("new_password")

        return data


class UserApprovalSerializer(serializers.Serializer):
    approve = serializers.BooleanField()

    def validate_approve(self, value):
        # You can add custom validation logic for the 'approve' field if needed
        return value


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=255)
    pincode = serializers.CharField(max_length=50)

