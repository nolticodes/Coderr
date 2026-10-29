from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Min

from offers_app.models import Offer

from .serializers import GetOffersListSerializer


class GetOffersListView(APIView):

    permission_classes = [AllowAny]

    queryset = Offer.objects.annotate(
        min_price=Min("details__price"),
        min_delivery_time=Min("details__delivery_time"),
    ).select_related('user').prefetch_related('details')

    def get(self, request):

        offers = self.queryset.all()

        serializer = GetOffersListSerializer(
            offers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
