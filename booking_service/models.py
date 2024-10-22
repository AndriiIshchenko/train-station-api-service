from django.db import models
from django.conf import settings


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

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
        return f"{self.name} {self.train_type}"


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

    def __str__(self) -> str:
        return f"{self.source} -> {self.distance}"


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

    def __str__(self) -> str:
        return f"{self.trip} cargo: {self.cargo} seat: {self.seat}"
