from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from booking_service.models import (
    Crew,
    Order,
    Route,
    Station,
    Ticket,
    Train,
    TrainType,
    Trip,
)
from booking_service.serializers import (
    CrewSerializer,
    OrderSerializer,
    RouteSerializer,
    StationSerializer,
    TicketSerializer,
    TrainTypeSerializer,
    TrainSerializer,
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


class TrainViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer


class RouteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class TripViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class TicketViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
