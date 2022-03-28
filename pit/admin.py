from django.contrib import admin
from .models import Sala, Equipo, Mesa, Slot, Reserva

admin.site.register(Sala)
admin.site.register(Equipo)
admin.site.register(Mesa)
admin.site.register(Slot)
admin.site.register(Reserva)