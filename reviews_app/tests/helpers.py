from rest_framework.authtoken.models import Token

from auth_app.models import User
from reviews_app.models import Reviews


def create_review_users():
    """Create two customers and two business users for review tests."""
    users = {}

    for username, user_type in [
        ("customer", "customer"),
        ("othercustomer", "customer"),
        ("business", "business"),
        ("otherbusiness", "business"),
    ]:
        users[username] = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="Testpasswort123!",
            type=user_type,
        )

    return users


def authenticate(client, user):
    """Authenticate the API client using the supplied user's token."""
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )


def create_review(business, reviewer, rating=4):
    """Create a review with explicit participants and a rating."""
    return Reviews.objects.create(
        business_user=business,
        reviewer=reviewer,
        rating=rating,
        description="Professional service.",
    )