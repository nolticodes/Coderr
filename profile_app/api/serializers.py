from rest_framework import serializers

from profile_app.models import Profile


class GetProfileDetailsSerializer(serializers.ModelSerializer):

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
        read_only=True
    )
    user = serializers.IntegerField(
        source="user.id",
        read_only=True
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

    email = serializers.EmailField(
        source="user.email"
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
        user_data = validated_data.pop("user", {})

        if "email" in user_data:
            user = instance.user
            user.email = user_data["email"]
            user.save(update_fields=["email"])

        return super().update(instance, validated_data)


class PatchProfileDetailsResponseSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    type = serializers.CharField(
        source="user.type",
        read_only=True
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

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    type = serializers.CharField(
        source="user.type",
        read_only=True
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

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    type = serializers.CharField(
        source="user.type",
        read_only=True
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
