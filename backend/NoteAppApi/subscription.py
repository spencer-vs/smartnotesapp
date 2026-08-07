from django.utils import timezone
from .models import Subscription

def has_premium_access(subscription):
    now = timezone.now()

    if (
        subscription.status == "trial"
        and subscription.trial_end <= now
    ):
        subscription.status = "expired"
        subscription.save(update_fields=["status"])
        return False

    if subscription.status == "active":
        if (
            subscription.subscription_end
            and subscription.subscription_end > now
        ):
            return True

        subscription.status = "expired"
        subscription.save(update_fields=["status"])
        return False

    return subscription.status == "trial"

def user_has_premium(user):
    subscription, _ = Subscription.objects.get_or_create(user=user)
    return has_premium_access(subscription)



# if not user_has_premium(request.user):
#     return Response(
#         {
#             "detail": "Your free trial has expired. Upgrade to continue using SmartNotes AI."
#         },
#         status=403,
#     )