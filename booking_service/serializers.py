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
    destination = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class TripListSerializer(serializers.ModelSerializer):
    train = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    route = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="route_name"
    )

    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class TripDetailSerializer(serializers.ModelSerializer):
    train = TrainDetailSerializer(many=False, read_only=True)
    route = RouteSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
            model = Trip
            fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip", "order")
