from auth_app.models import User
from profile_app.models import Profile


def create_user_with_profile(username, user_type="customer"):
    """Create a user and an associated profile with known values."""
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="Testpasswort123!",
        type=user_type,
    )

    profile = Profile.objects.create(
        user=user,
        first_name="Max",
        last_name="Mustermann",
        file="profile.jpg",
        location="Berlin",
        tel="123456789",
        description="Original description",
        working_hours="9-17",
    )

    return user, profile