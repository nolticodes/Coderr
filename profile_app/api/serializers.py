from rest_framework import serializers

from profile_app.models import Profile


class GetProfileDetailsSerializer(serializers.ModelSerializer):
    """Serialize profile details with linked user information."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    type = serializers.CharField(
        source="user.type",
        read_only=True,
    )
    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    created_at = serializers.DateTimeField(
        source="user.created_at",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]


class PatchProfileDetailsRequestSerializer(serializers.ModelSerializer):
    """Validate profile changes and updates to the linked user's email."""

    email = serializers.EmailField(
        source="user.email",
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
            "email",
        ]

    def update(self, instance, validated_data):
        """Update the linked user's email and save the remaining profile changes."""
        user_data = validated_data.pop("user", {})

        if "email" in user_data:
            user = instance.user
            user.email = user_data["email"]
            user.save(update_fields=["email"])

        return super().update(instance, validated_data)


class PatchProfileDetailsResponseSerializer(serializers.ModelSerializer):
    """Serialize the updated profile with linked user information."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    type = serializers.CharField(
        source="user.type",
        read_only=True,
    )
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    created_at = serializers.DateTimeField(
        source="user.created_at",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]


class GetBusinessProfilesSerializer(serializers.ModelSerializer):
    """Serialize business profile information with the user's name and type."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    type = serializers.CharField(
        source="user.type",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class GetCustomerProfilesSerializer(serializers.ModelSerializer):
    """Serialize customer profile information and the file upload timestamp."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    type = serializers.CharField(
        source="user.type",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]