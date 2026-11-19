from auth_app.models import User
from offers_app.models import Offer, OfferDetail
from orders_app.models import Orders


def create_order_test_data():
    """Create a customer, provider, offer, and package for order tests."""
    customer = User.objects.create_user(
        username="testcustomer",
        email="customer@example.com",
        password="Testpasswort123!",
        type="customer",
    )
    business = User.objects.create_user(
        username="testbusiness",
        email="business@example.com",
        password="Testpasswort123!",
        type="business",
    )

    offer = Offer.objects.create(
        user=business,
        title="Design offer",
        description="Professional design services.",
        image=None,
    )
    detail = OfferDetail.objects.create(
        offer=offer,
        title="Basic design",
        revisions=2,
        delivery_time=5,
        price=100,
        features=["Logo", "Business card"],
        offer_type="basic",
    )

    return customer, business, detail


def create_test_order(customer, business, detail):
    """Create an order containing a snapshot of the selected package."""
    return Orders.objects.create(
        customer_user=customer,
        business_user=business,
        offer_detail=detail,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time,
        price=detail.price,
        features=list(detail.features),
        offer_type=detail.offer_type,
        status="in_progress",
    )