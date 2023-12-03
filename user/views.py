from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, LoginSerializer, ChangePasswordSerializer
from rest_framework.permissions import AllowAny
from .models import User
from custom_lib.exceptions import MyException
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from custom_lib.decorators import *
from custom_lib.helper import create_swagger_params


Authorization = create_swagger_params('Authorization')

class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate email and username uniqueness
        try:
            name = serializer.validated_data.get('name')
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            if not (username and email and password):
                raise MyException("Please provide all details",
                                  status=status.HTTP_400_BAD_REQUEST)

            # Add email validation logic if needed

            if User.objects.filter(email=email).exists():
                raise MyException("User Already Exist. Please Login",
                                  status=status.HTTP_400_BAD_REQUEST)

            hashedd_password = make_password(password)

            new_user = User.objects.create(
                name=name, username=username, email=email, password=hashedd_password)

            serializer = RegistrationSerializer(new_user)
            return Response({'success': True, 'new_user': serializer.data}, status=status.HTTP_201_CREATED)

        except MyException as e:
            return Response({'error': str(e), 'status': e.status}, status=e.status)


class LoginAPIView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            if not email or not password:
                raise MyException("Please provide email or password",
                                  status=status.HTTP_400_BAD_REQUEST)

            # Use filter() to get the user or None if not found
            user = User.objects.filter(email=email).first()

            if not user:
                raise MyException("User not Exist.",
                                  status=status.HTTP_404_NOT_FOUND)

            hashedd_password = user.password

            if not check_password(password, hashedd_password):
                raise MyException("Wrong password",
                                  status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)

            return Response({'success': True, 'status': status.HTTP_200_OK, 'data': {
                'token': access_token,
                **serializer.data
            }})

        except Exception as e:
            return Response({'error': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
        

class GetAllUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # @swagger_auto_schema(
    #     manual_parameters=[Authorization]
    # )
    def get(self, request):
        try:
            # Retrieve all objects from the database
            header = request.META.get("Authorization")
            print("fgh")
            data = list(User.objects.values())
            data = {"name": "sagar"}

            return Response({'success': True, "status": status.HTTP_200_OK, 'data': data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})

        
        
class ChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            authorization_header = request.META
            print(authorization_header)

            if not authorization_header or not authorization_header.startswith('Bearer '):
                raise MyException("Invalid or missing Authorization header",
                                  status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            user = self.request.user
            print(user)

            if not check_password(old_password, user.password):
                raise MyException("Incorrect old password",
                                  status=status.HTTP_400_BAD_REQUEST)

            # Update the password
            user.password = make_password(new_password)
            user.save()

            # Revoke existing tokens (optional)
            RefreshToken.for_user(user).blacklist()

            # Generate new refresh token
            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)

            return Response({'success': True, 'status': status.HTTP_200_OK, 'data': {
                'token': access_token,
                'message': 'Password updated successfully',
            }})

        except Exception as e:
            return Response({'error': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
