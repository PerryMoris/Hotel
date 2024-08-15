from django.contrib import admin
from .models import *
from . import models

admin.site.register(Booked)
admin.site.register(Client)
admin.site.register(Category)
admin.site.register(Rooms)
admin.site.register(Payments)
admin.site.register(Service_Request)
admin.site.register(Cleaning)
admin.site.register(ClientChallenges)
admin.site.register(Kitchen_Items)
admin.site.register(Reservation)
admin.site.register(ReservationPayments)