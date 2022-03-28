from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from pit.models import Slot

class Command(BaseCommand):
    help = 'Crea slots en lote'

    def add_arguments(self, parser):
        parser.add_argument('hora_inicio', nargs='?', type=str)
        parser.add_argument('hora_fin', nargs='?', type=str)
        parser.add_argument('duracion_slot', nargs='?', type=int)

    def handle(self, *args, **kwargs):

        if kwargs['duracion_slot'] <= 0:
            raise CommandError("La duración del slot debe ser mayor que 0.")

        hinicio = datetime.strptime(kwargs['hora_inicio'], '%H:%M')
        hmax = datetime.strptime(kwargs['hora_fin'], '%H:%M')

        hfin = hinicio + timedelta(minutes=kwargs['duracion_slot'])
        while hfin <= hmax:
            slotobj = Slot.objects.filter(horainicio=hinicio, horafin=hfin)
            if slotobj.exists():
                self.stdout.write(self.style.NOTICE('Ya existe el slot {}-{}.'.format(datetime.strftime(hinicio, '%H:%M'), datetime.strftime(hfin, '%H:%M'))))
            else:
                Slot(horainicio=hinicio, horafin=hfin).save()
                self.stdout.write(self.style.SUCCESS('Slots {}-{} creado.'.format(datetime.strftime(hinicio, '%H:%M'), datetime.strftime(hfin, '%H:%M'))))
            hinicio = hfin
            hfin = hinicio + timedelta(minutes=kwargs['duracion_slot'])