from django.contrib import admin
from .models import Event, DiscountCode, Ticket

admin.site.register(Event)
admin.site.register(DiscountCode)
admin.site.register(Ticket)
