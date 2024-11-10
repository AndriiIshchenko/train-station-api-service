from datetime import datetime

from django.db.models import F, Count
from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

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
    StationDetailSerializer,
    StationSerializer,
    StationImageSerializer,
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


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StationDetailSerializer
        if self.action == "upload_image":
            return StationImageSerializer
        return StationSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        # permission_classes=[IsAminUser]
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image for specific station"""
        station = self.get_object()
        serializer = self.get_serializer(station, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    queryset = (
        Trip.objects.all()
        .select_related("train", "route__source", "route__destination")
        .annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets")
            )
        )
    )
    serializer_class = TripSerializer

    def get_queryset(self):
        """Retrieve the trips with filters"""
        date = self.request.query_params.get("departure_time")
        source_id_str = self.request.query_params.get("source")
        destination_id_str = self.request.query_params.get("destination")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date__gte=date)

        if source_id_str:
            queryset = queryset.filter(route__source__id=int(source_id_str))

        if destination_id_str:
            queryset = queryset.filter(route__destination__id=int(destination_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.INT,
                description="Filter by trip source id (ex. ?source=2)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.INT,
                description="Filter by trip destination id (ex. ?destination=2)",
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description=("Filter by datetime of Trip " "(ex. ?date=2022-10-23)"),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__trip__route__source",
        "tickets__trip__route__destination",
        "tickets__trip__train",
        "tickets__trip__crew",
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
