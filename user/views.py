from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserApprovalSerializer,
    UpdateProfileSerializer,
)
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
from .models import PageInfo, UserDetails
from custom_lib.api_call import api_call
import requests
from rest_framework.parsers import MultiPartParser, FormParser
import boto3
from botocore.exceptions import NoCredentialsError

import os

envs = os.environ
User = get_user_model()
Authorization = create_swagger_params("Authorization")


class RegistrationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["User"],
        request_body=RegistrationSerializer,
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate email and username uniqueness
        try:
            firstName = serializer.validated_data.get("first_name")
            lastName = serializer.validated_data.get("last_name")
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            if not (email and password and firstName and lastName):
                raise MyException(
                    "Please provide all details", status=status.HTTP_400_BAD_REQUEST
                )

            # Add email validation logic if needed

            if User.objects.filter(email=email).exists():
                raise MyException(
                    "User Already Exist. Please Login",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            hashedd_password = make_password(password)

            new_user = User.objects.create(
                first_name=firstName,
                last_name=lastName,
                username=email,
                is_superuser=0,
                is_active=0,
                email=email,
                password=hashedd_password,
            )

            serializer = RegistrationSerializer(new_user)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except MyException as e:
            return Response({"error": str(e), "status": e.status}, status=e.status)


class LoginAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["User"],
        request_body=LoginSerializer,
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            if not email or not password:
                raise MyException(
                    "Please provide email or password",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use get() instead of filter() to get the user or None if not found
            user = User.objects.get(email=email)

            if not user:
                raise MyException("User not Exist.", status=status.HTTP_404_NOT_FOUND)

            if not check_password(password, user.password):
                raise MyException("Wrong password", status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)
            access_token_payload = refresh.access_token.payload
            access_token_payload["userId"] = user.id

            user_detail_data = {}
            user_details = UserDetails.objects.filter(user_id=user.id).first()
            if not user_details:
                user_detail_data = {}
            else:
                user_detail_data = {
                    "image_url": user_details.image_url,
                    "category": user_details.category,
                    "address":user_details.address,
                    "mobile_number":user_details.mobile_number,
                    "city":user_details.city,
                    "state":user_details.state,
                    "country":user_details.country,
                    "pincode":user_details.pincode,
                }

            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "data": {
                        "user_id": user.id,
                        "token": access_token,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "email": user.email,
                        "is_staff": user.is_staff,
                        **user_detail_data
                    },
                }
            )

        except Exception as e:
            return Response(
                {"error": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}
            )


class GetAllUser(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User"], manual_parameters=[Authorization])
    def get(self, request):
        try:
            data = list(User.objects.values())

            return Response(
                {"success": True, "status": status.HTTP_200_OK, "data": data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e), "status": e.status})


class ChangePasswordAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["User"],
        request_body=ChangePasswordSerializer,
        manual_parameters=[Authorization],
    )
    def post(self, request):
        try:
            authorization_header = request.META

            if not authorization_header or not authorization_header.startswith(
                "Bearer "
            ):
                raise MyException(
                    "Invalid or missing Authorization header",
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            user = self.request.user

            if not check_password(old_password, user.password):
                raise MyException(
                    "Incorrect old password", status=status.HTTP_400_BAD_REQUEST
                )

            # Update the password
            user.password = make_password(new_password)
            user.save()

            # Revoke existing tokens (optional)
            RefreshToken.for_user(user).blacklist()

            # Generate new refresh token
            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)

            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "data": {
                        "token": access_token,
                        "message": "Password updated successfully",
                    },
                }
            )

        except Exception as e:
            return Response({"error": str(e), "status": e.status})


class ForgotPasswordAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["User"], request_body=ForgotPasswordSerializer)
    def post(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]

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
                Destination={"ToAddresses": to_email},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": message}},
                },
            )

            return Response(
                {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "message": "Password reset link sent successfully.",
                }
            )

        except Exception as e:
            return Response({"error": str(e), "status": status.HTTP_404_NOT_FOUND})


class ResetPasswordAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["User"], request_body=ResetPasswordSerializer)
    def post(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise MyException("Invalid user link.", status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                new_password = serializer.validated_data["new_password"]

                # Add any additional validation logic you need here

                user.set_password(new_password)
                user.save()

                return Response(
                    {
                        "success": True,
                        "status": status.HTTP_200_OK,
                        "message": "Password reset successfully.",
                    }
                )
            else:
                return Response(
                    {"error": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}
                )

        else:
            raise MyException("Invalid token.", status=status.HTTP_400_BAD_REQUEST)


class UserApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["User"],
        manual_parameters=[Authorization],
        request_body=UserApprovalSerializer,
    )
    def post(self, request, *args, **kwargs):
        try:
            user = self.request.user

            # Check if the current user is an admin
            if not user.is_staff:
                raise MyException(
                    "Permission denied. You must be an admin to approve users.",
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = UserApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            approve = serializer.validated_data["approve"]

            user_to_approve_id = kwargs.get("user_id")
            user_to_approve = User.objects.get(pk=user_to_approve_id)

            if approve:
                user_to_approve.is_active = True
                user_to_approve.save()
                return Response(
                    {
                        "success": True,
                        "status": status.HTTP_200_OK,
                        "message": "User approved successfully.",
                    }
                )
            else:
                # If you want to implement disapproval logic, you can add it here
                user_to_approve.is_active = False
                user_to_approve.save()
                return Response(
                    {
                        "success": True,
                        "status": status.HTTP_200_OK,
                        "message": "User disapproved successfully.",
                    }
                )

        except MyException as e:
            return Response({"error": str(e), "status": e.status}, status=e.status)


class GetVideoRevenue(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User"], manual_parameters=[Authorization])
    def get(self, request):
        try:
            user_id = request.user.id

            page_info_instance = PageInfo.objects.filter(user_id=user_id).first()

            if page_info_instance:
                page_access_token = page_info_instance.page_access_token

                page_id = page_info_instance.page_id

                # Make an API request to a third-party endpoint using the obtained access token
                all_video_api_url = f"https://graph.facebook.com/v18.0/{page_id}/videos?access_token={page_access_token}"

                api_request_result = api_call(
                    type="GET",  # Specify the HTTP method (GET, POST, etc.)
                    url=all_video_api_url,
                )

                def get_total_ad_earnings(video_id):
                    url = f"https://graph.facebook.com/v18.0/{video_id}/video_insights/total_video_ad_break_earnings?access_token={page_access_token}"

                    response = requests.get(url)
                    data = response.json()

                    if "data" in data:
                        total_earnings = sum(
                            entry["values"][0]["value"] for entry in data["data"]
                        )

                        return total_earnings
                    else:
                        return 0

                if api_request_result["success"]:
                    api_data = api_request_result["data"]
                    latest_20_video_ids = [
                        video["id"] for video in api_data["data"][:20]
                    ]
                    api_request_result = api_call(type="GET", url=all_video_api_url)

                    total_sum = sum(
                        get_total_ad_earnings(video_id)
                        for video_id in latest_20_video_ids
                    )

                    page_info = PageInfo.objects.filter(user_id=user_id)

                    update_data = {"facebook_earning": total_sum}

                    if not page_info.exists():
                        PageInfo.objects.create(user_id=user_id, **update_data)
                    else:
                        page_info.update(**update_data)

                    return Response(
                        {
                            "success": True,
                            "status": status.HTTP_200_OK,
                            "data": {"total_earning": total_sum},
                        },
                        status=status.HTTP_200_OK,
                    )

                else:
                    api_error = api_request_result["error"]
                    return Response(
                        {
                            "success": False,
                            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "data": api_error,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            else:
                return Response(
                    {
                        "success": False,
                        "status": status.HTTP_404_NOT_FOUND,
                        "data": "PageInfo not found for the user",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as e:
            return Response(
                {"error": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}
            )


class GetLatestVideo(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User"], manual_parameters=[Authorization])
    def get(self, request):
        try:
            user_id = request.user.id

            page_info_instance = PageInfo.objects.filter(user_id=user_id).first()

            if page_info_instance:
                page_access_token = page_info_instance.page_access_token

                page_id = page_info_instance.page_id

                # Make an API request to a third-party endpoint using the obtained access token
                api_url = f"https://graph.facebook.com/v18.0/{page_id}/videos?access_token={page_access_token}&fields=id,title,description,updated_time,views,permalink_url"

                api_request_result = api_call(
                    type="GET",  # Specify the HTTP method (GET, POST, etc.)
                    url=api_url,
                )

            if api_request_result["success"]:
                api_data = api_request_result["data"]["data"]

                return Response(
                    {"success": True, "status": status.HTTP_200_OK, "data": api_data},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"error": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}
            )


class UpdateProfileAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["User"],
        request_body=UpdateProfileSerializer,
        manual_parameters=[Authorization],
    )
    def post(self, request):
        try:
            user = self.request.user

            # Update data for User model
            update_data_user = {}
            if "first_name" in request.data:
                update_data_user["first_name"] = request.data["first_name"]
            if "last_name" in request.data:
                update_data_user["last_name"] = request.data["last_name"]
            if "email" in request.data:
                update_data_user["email"] = request.data["email"]
            if "password" in request.data:
                update_data_user["password"] = make_password(request.data["password"])

            User.objects.filter(id=user.id).update(**update_data_user)

            # Update data for UserDetails model
            update_data_user_details = {}
            if "mobile_number" in request.data:
                update_data_user_details["mobile_number"] = request.data[
                    "mobile_number"
                ]
            if "address" in request.data:
                update_data_user_details["address"] = request.data["address"]
            if "city" in request.data:
                update_data_user_details["city"] = request.data["city"]
            if "state" in request.data:
                update_data_user_details["state"] = request.data["state"]
            if "country" in request.data:
                update_data_user_details["country"] = request.data["country"]
            if "pincode" in request.data:
                update_data_user_details["pincode"] = request.data["pincode"]

            user_details = UserDetails.objects.filter(user_id=user.id)

            if not user_details.exists():
                UserDetails.objects.create(user_id=user.id, **update_data_user_details)
            else:
                user_details.update(**update_data_user_details)

            return Response(
                {"success": True, "message": "Profile updated successfully"},
                status=status.HTTP_200_OK,
            )

        except MyException as e:
            return Response({"error": str(e), "status": e.status}, status=e.status)


class GetUserDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User"], manual_parameters=[Authorization])
    def get(self, request):
        try:
            user_id = request.query_params.get("user_id")

            if not user_id:
                raise MyException("Please Provide user Id", 500)

            user_data = User.objects.filter(id=user_id).first()

            user_details_instance = UserDetails.objects.filter(user_id=user_id).first()

            user_details_data = {}

            if user_details_instance:
                user_details_data = {
                    "image_url":user_details_instance.image_url,
                    "user_id": user_details_instance.user_id,
                    "mobile_number": user_details_instance.mobile_number,
                    "address": user_details_instance.address,
                    "city": user_details_instance.city,
                    "state": user_details_instance.state,
                    "country": user_details_instance.country,
                    "pincode": user_details_instance.pincode,
                }
            else:
                pass

            user_data = {
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "email": user_data.email,
                "is_superuser": user_data.is_superuser,
                "is_staff": user_data.is_staff,
                "is_active": user_data.is_active,
            }
            user_data.update(user_details_data)

            return Response(
                {"success": True, "status": status.HTTP_200_OK, "data": user_data},
                status=status.HTTP_200_OK,
            )

        except MyException as e:
            return Response({"error": str(e), "status": e.status})
        except Exception as e:
            return Response(
                {"error": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}
            )


class UploadProfilePictureAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def validate_file(self, file):
        max_size_validator = 5 * 1024 * 1024  # 5 MB
        allowed_extensions = ["jpg", "jpeg", "png"]

        # Validate file extension
        file_extension = file.name.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise MyException(
                "Invalid file type. Only JPEG, JPG, and PNG allowed.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size
        if file.size > max_size_validator:
            raise MyException(
                "File size must be up to 5 MB.", status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        try:
            user = self.request.user

            profile_picture = request.FILES.get("profile_picture")
            if not profile_picture:
                raise MyException(
                    "Profile picture is required", status=status.HTTP_400_BAD_REQUEST
                )

            self.validate_file(profile_picture)

            # Generate a unique file name based on user information
            file_extension = profile_picture.name.split(".")[-1]
            folder_path = f"profile_pictures/"
            file_name = f"{folder_path}user_id_{user.id}.{file_extension}"

            # Upload the file to AWS S3 bucket
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3.upload_fileobj(profile_picture, bucket_name, file_name)

            # Generate the URL for the uploaded file
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

            user_details = UserDetails.objects.filter(user_id=user.id)

            if not user_details.exists():
                UserDetails.objects.create(user_id=user.id, image_url=s3_url)
            else:
                user_details.update(image_url=s3_url)

            return Response(
                {
                    "success": True,
                    "data": {"image_url": s3_url},
                    "message": "Profile picture uploaded successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except NoCredentialsError:
            return Response(
                {
                    "error": "AWS credentials not available",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except MyException as e:
            return Response({"error": str(e), "status": e.status}, status=e.status)


class UpdateEarningAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["User"],
        # request_body=UpdateProfileSerializer,
        # manual_parameters=[Authorization],
    )
    def post(self, request):
        try:
            user_id = request.data.get("user_id")

            if not user_id:
                raise MyException("Please Provide user Id", 500)

            update_data = {}
            if "page_access_token" in request.data:
                update_data["page_access_token"] = request.data["page_access_token"]
            if "page_id" in request.data:
                update_data["page_id"] = request.data["page_id"]
            if "snapchat_earning" in request.data:
                update_data["snapchat_earning"] = request.data["snapchat_earning"]
            if "instagram_earning" in request.data:
                update_data["instagram_earning"] = request.data["instagram_earning"]
            if "facebook_earning" in request.data:
                update_data["facebook_earning"] = request.data["facebook_earning"]
            if "youtube_earning" in request.data:
                update_data["youtube_earning"] = request.data["youtube_earning"]

            user_details = PageInfo.objects.filter(user_id=user_id)

            if not user_details.exists():
                PageInfo.objects.create(user_id=user_id, **update_data)
            else:
                user_details.update(**update_data)

            return Response(
                {"success": True, "message": "Earnings updated successfully"},
                status=status.HTTP_200_OK,
            )

        except MyException as e:
            return Response({"error": str(e), "status": e.status}, status=e.status)


class GetAllEarningsAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User"], manual_parameters=[Authorization])
    def get(self, request):
        try:
            user_id = request.query_params.get("user_id")

            if not user_id:
                raise MyException("Please Provide user Id", 500)

            user_data = PageInfo.objects.filter(user_id=user_id).first()

            if not user_data:
                raise MyException("Page Information Not Found", 404)

            user_data = {
                "page_access_token": user_data.page_access_token,
                "page_id": user_data.page_id,
                "youtube_earning": user_data.youtube_earning,
                "snapchat_earning": user_data.snapchat_earning,
                "instagram_earning": user_data.instagram_earning,
                "facebook_earning": user_data.facebook_earning,
                "total_earning": (
                    float(user_data.youtube_earning)
                    + float(user_data.facebook_earning)
                    + float(user_data.instagram_earning)
                ),
            }

            return Response(
                {"success": True, "status": status.HTTP_200_OK, "data": user_data},
                status=status.HTTP_200_OK,
            )

        except MyException as e:
            return Response({"error": str(e), "status": e.status})
        except Exception as e:
            return Response(
                {"error": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}
            )
