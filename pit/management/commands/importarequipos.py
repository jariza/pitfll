import csv
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from pit.models import Equipo, Sala

class Command(BaseCommand):
    help = 'Importa ID del equipo y el nombre desde un CSV con formato ID,Nombre,Nombre_sala_preferible'

    def add_arguments(self, parser):
        parser.add_argument('archivo', nargs='?', type=str)

    def handle(self, *args, **kwargs):

        with open(kwargs['archivo']) as fcsv:
            csv_reader = csv.reader(fcsv, delimiter=',')
            for row in csv_reader:
                if (len(row) > 0) and (len(row)) != 3:
                    self.stdout.write(self.style.WARNING("Se encontró una línea que no tiene 3 campos, se ignorará: {}").format(','.join(row)))
                elif len(row) == 3:
                    nombre = row[1]
                    idequipo = int(row[0])
                    objidsala = Sala.objects.filter(nombre=row[2])
                    if not objidsala.exists():
                        self.stdout.write(
                            self.style.WARNING("No se encontró sala con nombre {}, se ignorará esta línea: {}").format(row[2], ','.join(row)))
                    elif Equipo.objects.filter(nombre=nombre, idequipo=idequipo).exists():
                        self.stdout.write(self.style.NOTICE("El equipo {} con ID {} ya existe.").format(nombre, idequipo))
                    elif Equipo.objects.filter(idequipo=idequipo).exists():
                        self.stdout.write(self.style.NOTICE("Ya existe un equipo con ID {}.").format(idequipo))
                    elif Equipo.objects.filter(nombre=nombre).exists():
                        self.stdout.write(self.style.NOTICE("Ya existe un equipo con nombre {}.").format(nombre))
                    else:
                        Equipo(nombre=nombre, idequipo=idequipo, salapreferible=objidsala.first()).save()
                        self.stdout.write(self.style.SUCCESS("Equipo {} con ID {} añadido.").format(nombre, idequipo))
