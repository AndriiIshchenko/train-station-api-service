from django.urls import path, include
from rest_framework import routers

from booking_service.views import (
    CrewViewSet,
    OrderViewSet,
    RouteViewSet,
    StationViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    TripViewSet,
)


router = routers.DefaultRouter()

router.register("crew", CrewViewSet)
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("routes", RouteViewSet)
router.register("trips", TripViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "booking_service"
