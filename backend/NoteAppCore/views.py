from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserProfileSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from NoteAppApi.subscription import has_premium_access
from django.utils import timezone


User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account created"}, status=201)
        return Response(serializer.errors, status=400)
        
 
 
def expire_subscription_if_needed(subscription):
    now = timezone.now()

    if (
        subscription.status == "active"
        and subscription.subscription_end
        and subscription.subscription_end <= now
    ):
        subscription.status = "expired"
        subscription.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return subscription        
        
        
class UserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        subscription = request.user.subscription
        
        expire_subscription_if_needed(subscription)

        serializer = UserProfileSerializer(request.user)

        return Response(serializer.data)