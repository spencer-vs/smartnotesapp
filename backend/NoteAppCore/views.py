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
        
        
# class UserView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request):
        
#         subscription = request.user.subscription
        
#         expire_subscription_if_needed(subscription)

#         serializer = UserProfileSerializer(request.user)

#         return Response(serializer.data)



class UserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        subscription = request.user.subscription

        expire_subscription_if_needed(subscription)

        serializer = UserProfileSerializer(request.user)

        return Response(serializer.data)

    def patch(self, request):

        current_password = request.data.get("current_password")

        if not current_password:
            return Response(
                {"detail": "Current password is required."},
                status=400
            )

        if not request.user.check_password(current_password):
            return Response(
                {"detail": "Current password is incorrect."},
                status=400
            )

        allowed_fields = [
            "username",
            "email",
            "phone",
            "address",
        ]

        update_fields = {}

        for field in allowed_fields:
            if field in request.data:
                update_fields[field] = request.data[field]

        if not update_fields:
            return Response(
                {"detail": "No profile changes were provided."},
                status=400
            )

        if "email" in update_fields:
            email = update_fields["email"].strip()

            if not email:
                return Response(
                    {"detail": "Email cannot be empty."},
                    status=400
                )

            if User.objects.filter(
                email__iexact=email
            ).exclude(
                pk=request.user.pk
            ).exists():
                return Response(
                    {"detail": "This email is already in use."},
                    status=400
                )

            update_fields["email"] = email

        for field, value in update_fields.items():
            setattr(request.user, field, value)

        request.user.save()

        serializer = UserProfileSerializer(request.user)

        return Response(serializer.data, status=200)