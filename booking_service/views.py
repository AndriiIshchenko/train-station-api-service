from django.db.models import F, Count
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from booking_service.models import (
    Crew,
    Order,
    Route,
    Station,
    Train,
    TrainType,
    Trip,
)
from booking_service.serializers import (
    CrewSerializer,
    OrderListSerializer,
    OrderSerializer,
    RouteSerializer,
    StationSerializer,
    TrainDetailSerializer,
    TrainListSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    TripDetailSerializer,
    TripListSerializer,
    TripSerializer,
)


class CrewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class TrainTypeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Train.objects.all().select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retrieve":
            return TrainDetailSerializer
        return TrainSerializer


class RouteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer


class TripViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = (Trip.objects.all()
    .select_related("train", "route")
    .annotate(
        tickets_available=(
            F("train__cargo_num") * F("train__places_in_cargo")
            - Count("tickets")
        )
        )
    )
    serializer_class = TripSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__trip__route", "tickets__trip__train", "tickets__trip__crew"
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
