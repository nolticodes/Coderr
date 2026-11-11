from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.db.models import Avg

from reviews_app.models import Reviews
from auth_app.models import User
from offers_app.models import Offer


class GetBaseInfoView(APIView):
    def get(self, request):
        review_count = Reviews.objects.count()
        average_rating = Reviews.objects.aggregate(
            average=Avg("rating")
        )["average"]
        average_rating = (
            round(average_rating, 1)
            if average_rating is not None
            else 0.0
        )
        business_profile_count = User.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        response_data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )
