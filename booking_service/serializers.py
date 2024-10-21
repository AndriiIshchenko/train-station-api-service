from rest_framework import serializers

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


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.Serializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class RouteSerializer(serializers.Serializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class TripSerializer(serializers.Serializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class OrderSerializer(serializers.Serializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.Serializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip", "order")
