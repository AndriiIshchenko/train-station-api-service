import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db.models import F, Count

from rest_framework.test import APIClient
from rest_framework import status

from booking_service.models import Crew, Route, Station, Train, TrainType, Trip
from booking_service.serializers import TripDetailSerializer, TripListSerializer


TRIP_URL = reverse("booking_service:trip-list")
STATION_URL = reverse("booking_service:station-list")


def trip_detail_url(trip_id):
    return reverse("booking_service:trip-detail", args=[trip_id])


def station_detail_url(station_id):
    return reverse("booking_service:station-detail", args=[station_id])


def image_upload_url(station_id):
    """Return URL for station image upload"""
    return reverse("booking_service:station-upload-image", args=[station_id])


def sample_train_type(**params) -> TrainType:
    defaults = {
        "name": "Express",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


def sample_crew(**params) -> Crew:
    defaults = {
        "first_name": "Joe",
        "last_name": "Black",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_station(**params) -> Station:
    defaults = {
        "name": "Kyiv",
        "latitude": 1,
        "longitude": "1",
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_train(**params) -> Train:
    defaults = {
        "name": "Intercity",
        "cargo_num": 9,
        "places_in_cargo": "50",
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_route(**params) -> Route:
    defaults = {
        "distance": 500,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_trip(**params) -> Trip:
    defaults = {
        "departure_time": "2024-10-02 14:00:00",
        "arrival_time": "2024-10-02 14:00:00",
    }
    defaults.update(params)

    return Trip.objects.create(**defaults)


class SampleTripFull(TestCase):
    def setUp(self):
        self.train_full = sample_train(train_type=sample_train_type())
        self.route_full = sample_route(
            source=sample_station(), destination=sample_station(name="test")
        )
        self.payload_full = {
            "route": self.route_full,
            "crew": sample_crew(),
            "train": self.train_full(),
            "departure_time": "2024-11-02 14:00:00",
            "arrival_time": "2024-11-02 14:01:00",
        }


class UnauthenticatedBookingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRIP_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="test",
        )
        self.client.force_authenticate(self.user)

        self.crew1 = sample_crew()
        self.crew2 = sample_crew(first_name="Adam")
        self.crew3 = sample_crew(first_name="Eva")

        self.train_type1 = sample_train_type()
        self.train_type2 = sample_train_type(name="Hightspeed")
        self.train_type3 = sample_train_type(name="Lowspeed")

        self.train1 = sample_train(train_type=self.train_type1)
        self.train2 = sample_train(name="Test2", train_type=self.train_type2)
        self.train3 = sample_train(name="Test3", train_type=self.train_type3)

        self.station1 = sample_station()
        self.station2 = sample_station(name="Lviv")
        self.station3 = sample_station(name="Dnipro")

        self.route1 = sample_route(source=self.station1, destination=self.station3)
        self.route2 = sample_route(
            distance=400, source=self.station2, destination=self.station1
        )
        self.route3 = sample_route(
            distance=450, source=self.station3, destination=self.station2
        )

        self.trip1 = sample_trip(
            route=self.route1,
            train=self.train1,
        )
        self.trip2 = sample_trip(
            departure_time="2024-10-03 15:00:00",
            route=self.route2,
            train=self.train2,
        )
        self.trip3 = sample_trip(
            departure_time="2024-10-03 16:00:00",
            route=self.route3,
            train=self.train3,
        )
        self.queryset_all_trips = Trip.objects.all().annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets")
            )
        )

        self.serializer1 = TripListSerializer(self.queryset_all_trips.get(pk=1))
        self.serializer2 = TripListSerializer(self.queryset_all_trips.get(pk=2))
        self.serializer3 = TripListSerializer(self.queryset_all_trips.get(pk=3))

    def test_trip_list(self):
        res = self.client.get(TRIP_URL)
        trips = self.queryset_all_trips
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def asserts_for_test_filter(self, res, inverse=False):
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if inverse:
            self.assertNotIn(self.serializer1.data, res.data)
            self.assertIn(self.serializer2.data, res.data)
            self.assertIn(self.serializer3.data, res.data)
        else:
            self.assertIn(self.serializer1.data, res.data)
            self.assertNotIn(self.serializer2.data, res.data)
            self.assertNotIn(self.serializer3.data, res.data)

    def test_trip_list_filter_source(self):
        res = self.client.get(TRIP_URL, {"source": f"{self.station1.id}"})
        self.asserts_for_test_filter(res)

    def test_trip_list_filter_destination(self):
        res = self.client.get(TRIP_URL, {"destination": f"{self.station3.id}"})
        self.asserts_for_test_filter(res)

    def test_trip_list_filter_time(self):
        """
        Filter trips by departure time.
        The returned trips must be at the choosen time or later
        """
        res = self.client.get(TRIP_URL, {"departure_time": "2024-10-03"})

        self.asserts_for_test_filter(res, inverse=True)

    def test_retrieve_trip_detail(self):
        url = trip_detail_url(self.trip3.id)
        res = self.client.get(url)
        serializer = TripDetailSerializer(self.queryset_all_trips.get(pk=3))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_trip_forbidden(self):
        train_full = sample_train(
            name="test11", train_type=sample_train_type(name="test11")
        )
        route_full = sample_route(
            source=sample_station(name="test11"),
            destination=sample_station(name="test22"),
        )
        crew_full = sample_crew(first_name="test11")
        payload_full = {
            "route": route_full.id,
            "crew": crew_full.id,
            "train": train_full.id,
            "departure_time": "2024-11-02 14:00:00",
            "arrival_time": "2024-11-02 14:01:00",
        }
        res = self.client.post(TRIP_URL, payload_full)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTripTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="admin@test.com", password="password", is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        self.train_full = sample_train(train_type=sample_train_type())
        self.route_full = sample_route(
            source=sample_station(), destination=sample_station(name="test")
        )
        self.crew_full = sample_crew()
        self.payload_full = {
            "route": self.route_full.id,
            "crew": self.crew_full.id,
            "train": self.train_full.id,
            "departure_time": "2024-11-02 14:00:00",
            "arrival_time": "2024-11-02 14:01:00",
        }

    def test_create_trip(self):
        res = self.client.post(TRIP_URL, self.payload_full)
        print(f"Res {res}")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        trip = Trip.objects.get(pk=res.data["id"])

        self.assertEqual(self.route_full, trip.route)
        self.assertEqual(self.train_full, trip.train)
        self.assertIn(self.crew_full, trip.crew.all())

    def test_delete_trip_not_allowed(self):
        trip = sample_trip(
            route=sample_route(
                source=sample_station(name="test444"),
                destination=sample_station(name="test333"),
            ),
            train=sample_train(
                name="test444", train_type=sample_train_type(name="name555")
            ),
            departure_time="2024-11-02 14:00:00",
            arrival_time="2024-11-02 14:01:00",
        )

        url = trip_detail_url(trip.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class StationImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admin.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.station = sample_station(name="test_image")

    def tearDown(self):
        self.station.image.delete()

    def test_upload_image_to_station(self):
        """Test uploading an image to station"""
        url = image_upload_url(self.station.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.station.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.station.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.station.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_staion_list(self):
        url = STATION_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {"name": "Some station", "latitude": 1, "longitude": 1, "image": ntf},
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        station = Station.objects.get(name="Some station")
        self.assertFalse(station.image)

    def test_image_url_is_shown_on_station_detail(self):
        url = image_upload_url(self.station.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(station_detail_url(self.station.id))

        self.assertIn("image", res.data)

    def test_image_url_is_not_on_station_list(self):
        url = image_upload_url(self.station.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(STATION_URL)

        self.assertNotIn("image", res.data[0].keys())
