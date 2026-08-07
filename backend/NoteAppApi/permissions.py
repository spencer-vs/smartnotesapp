from rest_framework.permissions import BasePermission
from .models import Subscription
from .subscription import has_premium_access


class HasPremiumSubscription(BasePermission):
    message = (
        "Your free trial has expired. Upgrade to continue using SmartNotes AI."
    )

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        subscription, _ = Subscription.objects.get_or_create(
            user=request.user
        )

        return has_premium_access(subscription)