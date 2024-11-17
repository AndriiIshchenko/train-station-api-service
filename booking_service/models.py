import os
import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

def station_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("booking_service/uploads/stations/", filename)

class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(null=True, upload_to=station_image_file_path)

    def __str__(self) -> str:
        return self.name


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="trains",
    )

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self) -> str:
        return f"{self.name}"


class Route(models.Model):
    source = models.ForeignKey(
        Station, blank=False, on_delete=models.CASCADE, related_name="routes_source"
    )
    destination = models.ForeignKey(
        Station,
        blank=False,
        on_delete=models.CASCADE,
        related_name="routes_destination",
    )
    distance = models.IntegerField()

    @property
    def route_name(self):
        return f"{self.source.name} --> {self.destination.name}"

    def __str__(self) -> str:
        return f"{self.route_name}"


class Trip(models.Model):
    route = models.ForeignKey(
        Route, blank=False, on_delete=models.CASCADE, related_name="trips"
    )
    train = models.ForeignKey(
        Train, blank=False, on_delete=models.CASCADE, related_name="trips"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, blank=False, related_name="trips")

    def __str__(self) -> str:
        return f"{self.route} {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    trip = models.ForeignKey(
        Trip, blank=False, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, blank=False, on_delete=models.CASCADE, related_name="tickets"
    )
    cargo = models.IntegerField()
    seat = models.IntegerField()

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not 1 <= ticket_attr_value <= count_attrs:
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_value} is invalid -> "
                        f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
            ValidationError,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Ticket, self).save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.trip} cargo: {self.cargo} seat: {self.seat}"

    class Meta:
        unique_together = ("trip", "cargo", "seat")
        ordering = ["cargo", "seat"]
