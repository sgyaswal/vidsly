from rest_framework import serializers
from .models import User

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'username', 'password', 'email']
    
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
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        # You can add additional validation logic here if needed

        return data
