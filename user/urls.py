# user/urls.py

from django.urls import path
from .views import (
    RegistrationAPIView,
    LoginAPIView,
    GetAllUser,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    UserApprovalAPIView,
    GetVideoRevenue,
    GetLatestVideo,
    UpdateProfileAPIView,
    UploadProfilePictureAPIView,
    UpdateEarningAPIView,
    GetUserDetailsAPIView,
    GetAllEarningsAPIView
)

urlpatterns = [
    path("register", RegistrationAPIView.as_view(), name="register"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("getAllUser", GetAllUser.as_view(), name="getAllUser"),
    # path('changePassword', ChangePasswordAPIView.as_view(), name='change_password'),
    path("forgotPassword", ForgotPasswordAPIView.as_view(), name="forgot_password"),
    path(
        "resetPassword/<str:uidb64>/<str:token>",
        ResetPasswordAPIView.as_view(),
        name="reset-password",
    ),
    path(
        "userApproval/<int:user_id>",
        UserApprovalAPIView.as_view(),
        name="user-approval",
    ),
    path("getVideoRevenue", GetVideoRevenue.as_view(), name="get-VideoRevenue"),
    path("getlateastVideo", GetLatestVideo.as_view(), name="get-LateastVideo"),
    path("updateProfile", UpdateProfileAPIView.as_view(), name="update-profile"),
    path("updateProfilePicture", UploadProfilePictureAPIView.as_view(), name="update-profile-Picture"),
    path("updateEarning", UpdateEarningAPIView.as_view(), name="update-earning"),
    path('getUserDetails', GetUserDetailsAPIView.as_view(), name='get-user-details'),
    path('getAllEarnings', GetAllEarningsAPIView.as_view(), name='get-all-earnings'),
]
