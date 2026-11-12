from rest_framework import serializers
from auth_app.models import User
from profile_app.models import Profile


class RegistrationPostSerializer(serializers.ModelSerializer):
    """Validate registration data and create a user with a profile."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_email(self, value):
        """Reject an email address that is already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists!")
        return value

    def validate(self, attrs):
        """Ensure that the password and repeated password match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Password do not match!")
        return attrs

    def create(self, validated_data):
        """Create a user with a hashed password and an associated profile."""
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.username = validated_data["username"]
        user.email = validated_data["email"]
        user.type = validated_data["type"]
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """Validate the username and password fields supplied for login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
