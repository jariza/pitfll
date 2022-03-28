from django.db import models

class Sala(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Equipo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    idequipo = models.IntegerField(unique=True)
    salapreferible = models.ForeignKey(Sala, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('nombre', 'idequipo'),)

    def __str__(self):
        return "{} - {}".format(self.idequipo, self.nombre)

class Mesa(models.Model):
    nombre = models.CharField(max_length=4, unique=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Slot(models.Model):
    horainicio = models.TimeField()
    horafin = models.TimeField()

    class Meta:
        unique_together = (('horainicio', 'horafin'),)

    def __str__(self):
        return self.horainicio.strftime("%-H:%M") + "-" + self.horafin.strftime("%-H:%M")


class Reserva(models.Model):
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('slot', 'mesa'),)

    def __str__(self):
        return 'Equipo "{}" en la mesa {}, slot {}'.format(self.equipo, self.mesa, self.slot)
