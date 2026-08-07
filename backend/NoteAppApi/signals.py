from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Subscription
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import SubscriptionSerializer

User = get_user_model()



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    subscription, _ = Subscription.objects.get_or_create(user=request.user)
    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)