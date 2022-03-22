from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from .models import Equipo, Mesa, Slot, Reserva, Sala

class IndexView(generic.ListView):
    template_name = 'pit/index.html'
    context_object_name = 'datos'

    def get_queryset(self):
        #Reservas es (slot, mesa): equipo
        reservas = dict()
        for i in Reserva.objects.all():
            if i.slot.id not in reservas:
                reservas[i.slot.id] = dict()
            reservas[i.slot.id][i.mesa.id] = i.equipo
        print(Slot.objects.filter(horainicio__gte=datetime.now()).order_by("horainicio"))
        print(datetime.now())

        return {
            'mesas': Mesa.objects.all().order_by("nombre"),
            'slots': Slot.objects.filter(horainicio__gte=datetime.now()).order_by("horainicio"),
            'equipos': Equipo.objects.all().order_by("idequipo"),
            'salas': Sala.objects.all().order_by("nombre")
        }

def horario(request, sala):
    template = loader.get_template('pit/horario.html')

    salaobj = Sala.objects.filter(pk=sala)

    # Reservas es (slot, mesa): equipo
    reservas = dict()

    if salaobj.exists():
        reservaobj = Reserva.objects.filter(mesa__sala=salaobj.first())
        for i in reservaobj:
            if i.slot.id not in reservas:
                reservas[i.slot.id] = dict()
            reservas[i.slot.id][i.mesa.id] = i.equipo

        context = {
            'mesas': Mesa.objects.filter(sala=salaobj.first()).order_by("nombre"),
            'slots': Slot.objects.all().order_by("horainicio"),
            'reservas': reservas
        }
    else:
        reservaobj = Reserva.objects.all()
        for i in reservaobj:
            if i.slot.id not in reservas:
                reservas[i.slot.id] = dict()
            reservas[i.slot.id][i.mesa.id] = i.equipo

        context = {
            'mesas': Mesa.objects.all().order_by("nombre"),
            'slots': Slot.objects.all().order_by("horainicio"),
            'reservas': reservas
        }

    return HttpResponse(template.render(context, request))

def actualizarhorario(request):
    if request.method == 'GET':
        return HttpResponse(status=405)

    if request.method == 'POST':
        if not all(x in request.POST for x in ['mesa', 'slot', 'equipo']):
            messages.error(request, "Falta campo en el formulario")

        mesa = int(request.POST['mesa'])
        slot = int(request.POST['slot'])
        equipo = int(request.POST['equipo'])

        mesaobj = Mesa.objects.filter(pk=mesa)
        slotobj = Slot.objects.filter(pk=slot)
        reserva_actual = Reserva.objects.filter(mesa=mesa, slot=slot)

        if equipo == -1:
            if reserva_actual.exists():
                mensaje = 'Se va a liberar el slot {} de la mesa {}, actualmente asignado al equipo "{}".'.format(slotobj.first(), mesaobj.first(), reserva_actual.first().equipo)
            else:
                mensaje = ''
                messages.info(request, 'El slot {} de la mesa {} está libre actualmente, no hay nada que cambiar nada.'.format(slotobj.first(), mesaobj.first()))
        else:
            equipoobj = Equipo.objects.filter(pk=equipo)

            reserva_futura = Reserva.objects.filter(equipo=equipo, slot__horainicio__gt=datetime.now())
            if reserva_futura.exists():
                reserva_futura_txt = ' OjO: El equipo ya tiene reserva en el slot {} de la mesa {}.'.format(reserva_futura.first().slot, reserva_futura.first().mesa)
            else:
                reserva_futura_txt = ''

            if reserva_actual.exists():
                if equipoobj.first().id == reserva_actual.first().equipo.id:
                    mensaje = ''
                    messages.info(request, 'El slot {} de la mesa {} ya estaba asignado al equipo "{}", no hay que cambiar nada.'.format(slotobj.first(), mesaobj.first(), equipoobj.first()))
                else:
                    mensaje = 'Slot {} de la mesa {} actualmente asignado al equipo "{}", se va a reasignar al equipo "{}".{}'.format(reserva_actual.first(), reserva_actual.first().mesa, reserva_actual.first().equipo, equipoobj.first(), reserva_futura_txt)
            else:
                mensaje = 'Se va a asignar el slot {} de la mesa {} al equipo "{}".{}'.format(slotobj.first(), mesaobj.first(), equipoobj.first(), reserva_futura_txt)

        template = loader.get_template('pit/actualizarhorario.html')
        context = {
            'mesa': mesa,
            'slot': slot,
            'equipo': equipo,
            'mensaje': mensaje
        }
        if mensaje == '':
            #Caso redundante, no hay nada que hacer
            return HttpResponseRedirect(reverse('pit:index'))
        else:
            return HttpResponse(template.render(context, request))

def confirmarhorario(request):
    if request.method == 'GET':
        return HttpResponse(status=405)

    if request.method == 'POST':
        if not all(x in request.POST for x in ['mesa', 'slot', 'equipo']):
            messages.error(request, "Falta campo en el formulario")

        mesa = int(request.POST['mesa'])
        slot = int(request.POST['slot'])
        equipo = int(request.POST['equipo'])

        if equipo == -1:
            Reserva.objects.filter(mesa=Mesa.objects.get(pk=mesa), slot=Slot.objects.get(pk=slot)).delete()
        else:
            Reserva(mesa=Mesa.objects.get(pk=mesa), slot=Slot.objects.get(pk=slot), equipo=Equipo.objects.get(pk=equipo)).save()

        return HttpResponseRedirect(reverse('pit:index'))
