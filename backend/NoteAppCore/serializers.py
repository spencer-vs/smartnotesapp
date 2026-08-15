from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from NoteAppApi.serializers import SubscriptionSerializer
User = get_user_model()



class RegisterSerializer(serializers.ModelSerializer):

    phone = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "phone",
            "address",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_username(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters."
            )

        return value

    def validate_password(self, value):

        if not re.search(r"[A-Za-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one letter."
            )

        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters."
            )

        return value

    def validate_phone(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) != 11:
            raise serializers.ValidationError(
                "Phone number must be exactly 11 digits."
            )

        return value

    def validate_email(self, value):
        return value.strip().lower()

    def validate_address(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Address is required."
            )

        return value.strip()

    def create(self, validated_data):

        phone = validated_data.pop("phone")
        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.phone = phone

        user.save()

        return user
    
    
    


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):

    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone",
            "address",
            "subscription",
        ]