from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Min
from django.db.models import Q

from offers_app.models import Offer, OfferDetail

from .serializers import (
    GetOffersListSerializer,
    PostNewOfferRequestSerializer,
    PostNewOfferResponseSerializer,
    GetOfferDetailsSerializer,
    PatchOfferDetailsRequestSerializer,
    OfferStatsSerializer,
)

from .pagination import OffersPagination

from .permissions import IsBusinessUser, IsAuthenticatedAndOwnerOrReadOnly


class OfferListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsBusinessUser]
    serializer_class = GetOffersListSerializer
    pagination_class = OffersPagination

    queryset = (
        Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time"),
        )
        .select_related("user")
        .prefetch_related("details")
        .order_by("id")
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetOffersListSerializer

        if self.request.method == "POST":
            return PostNewOfferRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        creator_id_param = self.request.query_params.get("creator_id")
        if creator_id_param is not None:
            queryset = queryset.filter(user_id=creator_id_param)

        min_price_param = self.request.query_params.get("min_price")
        if min_price_param is not None:
            queryset = queryset.filter(min_price__gte=min_price_param)

        max_delivery_time = self.request.query_params.get("max_delivery_time")
        if max_delivery_time is not None:
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        response_serializer = PostNewOfferResponseSerializer(
            serializer.instance,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class OfferDetailsListCreateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]
    serializer_class = GetOfferDetailsSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    queryset = (
        Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time"),
        )
        .select_related("user")
        .prefetch_related("details")
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetOfferDetailsSerializer

        if self.request.method == "PATCH":
            return PatchOfferDetailsRequestSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)

        response_serializer = PostNewOfferResponseSerializer(
                    serializer.instance,
                )
        
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class SpecificOfferDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OfferStatsSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    queryset = OfferDetail.objects.all()
