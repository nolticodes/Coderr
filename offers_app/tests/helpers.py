from auth_app.models import User
from offers_app.api.serializers import PostNewOfferRequestSerializer


def create_business_user():
    """Create a business user for offer serializer tests."""
    return User.objects.create_user(
        username="testbusiness",
        email="business@example.com",
        password="Testpasswort123!",
        type="business",
    )


def build_offer_data():
    """Return fresh offer input with three packages and omitted revisions."""
    return {
        "title": "Design offer",
        "image": None,
        "description": "Professional design services.",
        "details": [
            {
                "title": "Basic",
                "delivery_time_in_days": 5,
                "price": 100,
                "features": ["Logo"],
                "offer_type": "basic",
            },
            {
                "title": "Standard",
                "delivery_time_in_days": 7,
                "price": 200,
                "features": ["Logo", "Business card"],
                "offer_type": "standard",
            },
            {
                "title": "Premium",
                "delivery_time_in_days": 10,
                "price": 300,
                "features": ["Logo", "Business card", "Flyer"],
                "offer_type": "premium",
            },
        ],
    }


def create_offer(user):
    """Create an offer with three packages through the request serializer."""
    serializer = PostNewOfferRequestSerializer(
        data=build_offer_data()
    )
    serializer.is_valid(raise_exception=True)
    return serializer.save(user=user)