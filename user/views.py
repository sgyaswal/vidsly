from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, LoginSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserApprovalSerializer
from rest_framework.permissions import AllowAny
from custom_lib.exceptions import MyException
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import IsAuthenticated
from custom_lib.decorators import *
from custom_lib.helper import create_swagger_params
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from custom_lib.aws_utils import get_ses_client
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode


import os
envs = os.environ
User = get_user_model()
Authorization = create_swagger_params('Authorization')



class RegistrationAPIView(generics.CreateAPIView):
    
    permission_classes = [AllowAny]
    @swagger_auto_schema(
    tags=['User'],
    request_body=RegistrationSerializer,
    )

    

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate email and username uniqueness
        try:
            firstName = serializer.validated_data.get('first_name')
            lastName = serializer.validated_data.get('last_name')
            username = serializer.validated_data.get('email')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            if not (username and email and password and firstName and lastName):
                raise MyException("Please provide all details",
                                  status=status.HTTP_400_BAD_REQUEST)

            # Add email validation logic if needed

            if User.objects.filter(email=email).exists():
                raise MyException("User Already Exist. Please Login",
                                  status=status.HTTP_400_BAD_REQUEST)

            hashedd_password = make_password(password)

            new_user = User.objects.create(
                first_name=firstName, last_name=lastName, is_superuser=0, is_active=0, email=email, password=hashedd_password)

            serializer = RegistrationSerializer(new_user)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)

        except MyException as e:
            return Response({'error': str(e), 'status': e.status}, status=e.status)


class LoginAPIView(generics.CreateAPIView):

    permission_classes = [AllowAny]
    @swagger_auto_schema(
    tags=['User'],
    request_body=LoginSerializer,
    )

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            if not email or not password:
                raise MyException("Please provide email or password", status=status.HTTP_400_BAD_REQUEST)

            # Use get() instead of filter() to get the user or None if not found
            user = User.objects.get(email=email)


            if not user:
                raise MyException("User not Exist.", status=status.HTTP_404_NOT_FOUND)
            

            if not check_password(password, user.password):
                raise MyException("Wrong password", status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)
            access_token_payload = refresh.access_token.payload
            access_token_payload['userId'] = user.id

            return Response({'success': True, 'status': status.HTTP_200_OK, 'data': {
                'token': access_token,
            }})

        except Exception as e:
            return Response({'error': str(e), 'status': e.status})
        

class GetAllUser(APIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
    tags=['User'],
    manual_parameters=[Authorization]
    )

    def get(self, request):
        try:
            data = list(User.objects.values())

            return Response({'success': True, "status": status.HTTP_200_OK, 'data': data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e), 'status': e.status})

        
        
class ChangePasswordAPIView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
    tags=['User'],
    request_body=ChangePasswordSerializer,
    manual_parameters=[Authorization]
    )
    

    def post(self, request):
        try:

            authorization_header = request.META

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
            return Response({'error': str(e), 'status': e.status})
        

class ForgotPasswordAPIView(generics.CreateAPIView):

    permission_classes = [AllowAny]
    @swagger_auto_schema(
    tags=['User'],
    request_body=ForgotPasswordSerializer
    )

    def post(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise MyException("User not found.", status=status.HTTP_404_NOT_FOUND)

            token = default_token_generator.make_token(user)

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"https://yourdomain.com/reset-password/{uidb64}/{token}/"

            # Get the SES client using the generalized function
            ses = get_ses_client()

            subject = "Password Reset Request"
            message = f"Click the following link to reset your password: {reset_link}"
            from_email = settings.AWS_SES_VERIFY_EMAIL
            to_email = [user.email]

            # Send email using AWS SES
            ses.send_email(
                Source=from_email,
                Destination={'ToAddresses': to_email},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': message}},
                }
            )

            return Response({'success': True, 'status': status.HTTP_200_OK, 'message': 'Password reset link sent successfully.'})

        except Exception as e:
            return Response({'error': str(e), 'status': e.status})



class ResetPasswordAPIView(generics.CreateAPIView):

    permission_classes = [AllowAny]
    @swagger_auto_schema(
    tags=['User'],
    request_body=ResetPasswordSerializer
    )

    def post(self, request, uidb64, token):
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                raise MyException("Invalid user link.", status=status.HTTP_400_BAD_REQUEST)

            if default_token_generator.check_token(user, token):
                serializer = ResetPasswordSerializer(data=request.data)
                if serializer.is_valid():
                    new_password = serializer.validated_data['new_password']

                    # Add any additional validation logic you need here

                    user.set_password(new_password)
                    user.save()

                    return Response({'success': True, 'status': status.HTTP_200_OK, 'message': 'Password reset successfully.'})
                else:
                    return Response({'error': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST})

            else:
                raise MyException("Invalid token.", status=status.HTTP_400_BAD_REQUEST)

class UserApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
    tags=['User'],
    manual_parameters=[Authorization],
    request_body=UserApprovalSerializer
    )

    def post(self, request, *args, **kwargs):
        try:
            user = self.request.user

            # Check if the current user is an admin
            if not user.is_staff:
                raise MyException("Permission denied. You must be an admin to approve users.",
                                  status=status.HTTP_403_FORBIDDEN)

            serializer = UserApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            approve = serializer.validated_data['approve']

            user_to_approve_id = kwargs.get('user_id')
            user_to_approve = User.objects.get(pk=user_to_approve_id)

            if approve:
                user_to_approve.is_active = True
                user_to_approve.save()
                return Response({'success': True, 'status': status.HTTP_200_OK, 'message': 'User approved successfully.'})
            else:
                # If you want to implement disapproval logic, you can add it here
                user_to_approve.is_active = False
                user_to_approve.save()
                return Response({'success': True, 'status': status.HTTP_200_OK, 'message': 'User disapproved successfully.'})

        except MyException as e:
            return Response({'error': str(e), 'status': e.status}, status=e.status)
