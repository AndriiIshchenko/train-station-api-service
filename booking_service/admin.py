from django.contrib import admin

from .models import (
    Route,
    Crew,
    Ticket,
    Train,
    TrainType,
    Order,
    Trip,
    Station,
)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Ticket)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Order)
admin.site.register(Trip)
admin.site.register(Station)
