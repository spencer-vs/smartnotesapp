from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    PackagePurchase,
    UserCreditBalance,
    CreditTransaction,
)


FEATURE_BALANCE_FIELDS = {
    "audio": "audio_credits",
    "youtube": "youtube_credits",
    "quiz": "quiz_credits",
}


class InsufficientCredits(Exception):
    """Raised when a user does not have enough credits."""
    pass


def get_or_create_credit_balance(user):
    """
    Return the user's credit balance, creating it if necessary.

    Lock the user row first to help serialize balance creation
    and credit updates for the same user.
    """
    user.__class__.objects.select_for_update().get(pk=user.pk)

    balance, _ = UserCreditBalance.objects.get_or_create(
        user=user
    )

    return balance


@transaction.atomic
def grant_package_credits(purchase_id):
    """
    Grant package credits for a verified purchase.

    Returns True if credits were granted.
    Returns False if the purchase had already been credited.

    This function does not verify a Google Play purchase.
    Purchase verification must happen before calling it.
    """

    purchase = (
        PackagePurchase.objects
        .select_for_update()
        .select_related("package")
        .get(pk=purchase_id)
    )

    if purchase.status != "verified":
        raise ValidationError(
            "Credits can only be granted for verified purchases."
        )

    # Lock the user row before changing the user's balances.
    purchase.user.__class__.objects.select_for_update().get(
        pk=purchase.user_id
    )

    balance, _ = UserCreditBalance.objects.get_or_create(
        user_id=purchase.user_id
    )

    credit_amounts = {
        "audio": purchase.package.audio_credits,
        "youtube": purchase.package.youtube_credits,
        "quiz": purchase.package.quiz_credits,
    }

    # Each purchase gets a stable transaction key for each feature.
    transaction_keys = [
        f"purchase:{purchase.pk}:{feature}"
        for feature, amount in credit_amounts.items()
        if amount > 0
    ]

    existing_transactions = CreditTransaction.objects.filter(
        idempotency_key__in=transaction_keys
    )

    existing_keys = set(
        existing_transactions.values_list(
            "idempotency_key",
            flat=True,
        )
    )

    expected_keys = set(transaction_keys)

    if existing_keys == expected_keys:
        # Every credit addition already exists.
        return False

    if existing_keys:
        # A partial grant should never happen because the operation
        # is atomic. Stop rather than risking duplicate credits.
        raise ValidationError(
            "Inconsistent purchase credit history. "
            "Manual review is required."
        )

    for feature, amount in credit_amounts.items():
        if amount <= 0:
            continue

        balance_field = FEATURE_BALANCE_FIELDS[feature]

        new_balance = getattr(balance, balance_field) + amount

        setattr(balance, balance_field, new_balance)

        CreditTransaction.objects.create(
            user_id=purchase.user_id,
            purchase=purchase,
            transaction_type="purchase",
            feature=feature,
            amount=amount,
            balance_after=new_balance,
            description=(
                f"Credits from {purchase.package}"
            ),
            idempotency_key=(
                f"purchase:{purchase.pk}:{feature}"
            ),
        )

    balance.save(
        update_fields=[
            "audio_credits",
            "youtube_credits",
            "quiz_credits",
            "updated_at",
        ]
    )

    return True


@transaction.atomic
def consume_credit(user, feature, idempotency_key):
    """
    Deduct one credit for audio, YouTube, or quiz usage.

    The idempotency key identifies one logical operation. If the
    same operation is retried, it will not deduct a second credit.

    Returns:
        (transaction_record, already_processed)
    """

    if feature not in FEATURE_BALANCE_FIELDS:
        raise ValidationError(
            "Invalid feature. Use audio, youtube, or quiz."
        )

    if not idempotency_key or not idempotency_key.strip():
        raise ValidationError(
            "An idempotency key is required."
        )

    # Serialize balance changes for this user.
    user.__class__.objects.select_for_update().get(pk=user.pk)

    existing_transaction = CreditTransaction.objects.filter(
        idempotency_key=idempotency_key
    ).first()

    if existing_transaction:
        if (
            existing_transaction.user_id != user.pk
            or existing_transaction.feature != feature
            or existing_transaction.transaction_type != "usage"
        ):
            raise ValidationError(
                "This idempotency key has already been used "
                "for a different transaction."
            )

        return existing_transaction, True

    balance, _ = UserCreditBalance.objects.get_or_create(
        user=user
    )

    balance_field = FEATURE_BALANCE_FIELDS[feature]
    current_balance = getattr(balance, balance_field)

    if current_balance < 1:
        raise InsufficientCredits(
            f"You have no {feature} credits remaining."
        )

    new_balance = current_balance - 1

    setattr(balance, balance_field, new_balance)

    balance.save(
        update_fields=[
            balance_field,
            "updated_at",
        ]
    )

    credit_transaction = CreditTransaction.objects.create(
        user=user,
        transaction_type="usage",
        feature=feature,
        amount=-1,
        balance_after=new_balance,
        description=f"{feature.title()} credit used",
        idempotency_key=idempotency_key,
    )

    return credit_transaction, False





@transaction.atomic
def refund_credit(
    user,
    feature,
    usage_idempotency_key,
    refund_idempotency_key,
    description="Credit refunded after failed processing",
):
    """
    Refund one credit for a failed operation.

    A refund is allowed only when the matching usage transaction
    exists. Repeating the same refund request will not add credits
    again.

    Returns:
        (transaction_record, already_processed)
    """

    if feature not in FEATURE_BALANCE_FIELDS:
        raise ValidationError(
            "Invalid feature. Use audio, youtube, or quiz."
        )

    if not usage_idempotency_key or not usage_idempotency_key.strip():
        raise ValidationError(
            "The original usage transaction key is required."
        )

    if not refund_idempotency_key or not refund_idempotency_key.strip():
        raise ValidationError(
            "A refund idempotency key is required."
        )

    # Lock the user first so balance changes are serialized.
    user.__class__.objects.select_for_update().get(pk=user.pk)

    # Check whether this refund has already been processed.
    existing_refund = CreditTransaction.objects.filter(
        idempotency_key=refund_idempotency_key
    ).first()

    if existing_refund:
        if (
            existing_refund.user_id != user.pk
            or existing_refund.feature != feature
            or existing_refund.transaction_type != "refund"
            or existing_refund.amount != 1
        ):
            raise ValidationError(
                "This refund key has already been used "
                "for a different transaction."
            )

        return existing_refund, True

    # Locate the original credit deduction.
    usage_transaction = (
        CreditTransaction.objects
        .select_for_update()
        .filter(idempotency_key=usage_idempotency_key)
        .first()
    )

    if not usage_transaction:
        raise ValidationError(
            "The original credit deduction was not found."
        )

    if (
        usage_transaction.user_id != user.pk
        or usage_transaction.feature != feature
        or usage_transaction.transaction_type != "usage"
        or usage_transaction.amount != -1
    ):
        raise ValidationError(
            "The original transaction cannot be refunded."
        )

    # Lock the user's balance before updating it.
    balance, _ = UserCreditBalance.objects.get_or_create(
        user=user
    )

    balance = (
        UserCreditBalance.objects
        .select_for_update()
        .get(user=user)
    )

    balance_field = FEATURE_BALANCE_FIELDS[feature]
    new_balance = getattr(balance, balance_field) + 1

    setattr(balance, balance_field, new_balance)

    balance.save(
        update_fields=[
            balance_field,
            "updated_at",
        ]
    )

    refund_transaction = CreditTransaction.objects.create(
        user=user,
        transaction_type="refund",
        feature=feature,
        amount=1,
        balance_after=new_balance,
        description=description,
        idempotency_key=refund_idempotency_key,
    )

    return refund_transaction, False