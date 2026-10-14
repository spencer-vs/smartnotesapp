from rest_framework.permissions import BasePermission
from .models import Subscription
from .subscription import has_premium_access
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings



class HasTestingAccess(BasePermission):
    """
    Temporary permission for authorized SmartNotes beta testers.

    Testing access is granted only when:
    1. Global beta testing is enabled.
    2. The authenticated user is marked as a beta tester.
    """

    message = {
        "detail": "You need an authorized SmartNotes testing account.",
        "code": "testing_access_required",
    }

    def has_permission(self, request, view):

        user = request.user
        
        
       

        # Require authentication.
        if not user or not user.is_authenticated:
            return False

        # Testing mode must be enabled globally.
        if not getattr(settings, "BETA_TESTING_ENABLED", False):
            raise PermissionDenied({
                "detail": (
                    "Testing access is currently unavailable. "
                    "Package credits will be required when "
                    "the new access system is enabled."
                ),
                "code": "testing_disabled",
            })

        # Only approved beta testers receive free access.
        if getattr(user, "is_beta_tester", False):
            return True

        raise PermissionDenied({
            "detail": (
                "Your account is not authorized for "
                "the SmartNotes testing programme."
            ),
            "code": "testing_access_required",
        })


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
            subscription.cancel_at_period_end = False

            subscription.save(
               update_fields=[
                "status",
                "cancel_at_period_end",
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
            subscription.cancel_at_period_end = False

            subscription.save(
               update_fields=[
                 "status",
                 "cancel_at_period_end",
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