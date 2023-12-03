from custom_lib.authentication import BoAuthentication,ConsumerAuthentication,ClientAuthentication
from custom_lib.custom_mixin import LoggingMixin
from rest_framework.views import APIView
from custom_lib.permissions import DashboardPermission,ClientPermission

class ConsumerAPIView(LoggingMixin,APIView):
    permission_classes=(DashboardPermission,)
    authentication_classes = [ConsumerAuthentication]
    # renderer_classes = [JSONResponseRenderer]

class BoAPIView(LoggingMixin,APIView):
    permission_classes=(DashboardPermission,)
    authentication_classes = [BoAuthentication]

class ClientAPIView(LoggingMixin,APIView):
    permission_classes=(ClientPermission,)
    authentication_classes = [ClientAuthentication]

class CallbackAPIView(LoggingMixin,APIView):
    permission_classes=()
    authentication_classes = []

class CustomAPIView(LoggingMixin,APIView):
    permission_classes=()
    authentication_classes=[]
