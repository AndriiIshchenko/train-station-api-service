from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainListSerializer(serializers.ModelSerializer):
    train_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainDetailSerializer(serializers.ModelSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=False)

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "train", "route", "departure_time", "arrival_time", "crew")


class TripListSerializer(TripSerializer):
    train_name = serializers.CharField(source="train.name", read_only=True)
    route_name = serializers.CharField(source="route.route_name", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "route_name",
            "train_name",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class TripDetailSerializer(serializers.ModelSerializer):
    train = TrainDetailSerializer(many=False, read_only=True)
    route = RouteSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"], attrs["seat"], attrs["trip"].train, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip")


class TicketListSerializer(TicketSerializer):
    trip = TripListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
