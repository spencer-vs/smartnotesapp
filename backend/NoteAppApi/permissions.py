from rest_framework.permissions import BasePermission
from .models import Subscription
from .subscription import has_premium_access
from ..NoteAppCore.views import expire_subscription_if_needed
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone



class HasPremiumSubscription(BasePermission):

    def has_permission(self, request, view):

        try:
            subscription = request.user.subscription

        except Exception:
            raise PermissionDenied({
                "detail": (
                    "You need a SmartNotes Premium subscription "
                    "to use this feature."
                ),
                "code": "subscription_required",
            })

        now = timezone.now()

        # -----------------------------------
        # Automatically expire old subscription
        # -----------------------------------

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

        # -----------------------------------
        # Active trial
        # -----------------------------------

        if subscription.status == "trial":

            if subscription.trial_end > now:
                return True

            # Trial has expired
            subscription.status = "expired"
            subscription.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            raise PermissionDenied({
                "detail": (
                    "Your free trial has expired. "
                    "Upgrade to Premium to continue using "
                    "SmartNotes AI features."
                ),
                "code": "trial_expired",
            })

        # -----------------------------------
        # Active subscription
        # -----------------------------------

        if subscription.status == "active":

            if (
                subscription.subscription_end
                and subscription.subscription_end > now
            ):
                return True

        # -----------------------------------
        # Expired subscription
        # -----------------------------------

        if subscription.status == "expired":

            raise PermissionDenied({
                "detail": (
                    "Your subscription has expired. "
                    "Upgrade your plan to continue using "
                    "this feature."
                ),
                "code": "subscription_expired",
            })

        # -----------------------------------
        # Cancelled subscription
        # -----------------------------------

        if subscription.status == "cancelled":

            raise PermissionDenied({
                "detail": (
                    "Your subscription is no longer active. "
                    "Please choose a new plan to continue."
                ),
                "code": "subscription_cancelled",
            })

        # -----------------------------------
        # Anything else
        # -----------------------------------

        raise PermissionDenied({
            "detail": (
                "This feature requires an active "
                "SmartNotes Premium subscription."
            ),
            "code": "subscription_required",
        })