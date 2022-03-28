from datetime import datetime, timedelta
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.views.decorators.cache import never_cache
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

        return {
            'mesas': Mesa.objects.all().order_by("nombre"),
            'slots': Slot.objects.filter(horainicio__gte=datetime.now()).order_by("horainicio"),
            'equipos': Equipo.objects.all().order_by("idequipo"),
            'salas': Sala.objects.all().order_by("nombre"),
            'fechahoraservidor': datetime.now()
        }

def recursos(request):
    template = loader.get_template('pit/recursos.html')

    context = {
        'salas': Sala.objects.all().order_by("nombre")
    }

    return HttpResponse(template.render(context, request))

# sala, sala a mostrar, 0 para todas
# numslots, número de slots a mostrar, 0 para no limitar
# direccion, 1 para mostrar el horario pasado (por defecto va hacia el futuro)
def _tabla_horario_futuro(sala, numslots, pasado=0):

    # Datos de DB necesarios
    salaobj = Sala.objects.filter(pk=sala)
    # Se muetran slots desde hace 5 minutos
    if pasado == 1:
        slots = Slot.objects.filter(horafin__lte=datetime.now()).order_by("horainicio")
    else:
        slots = Slot.objects.filter(horafin__gte=(datetime.now() - timedelta(minutes=5))).order_by("horainicio")

    # Reservas es (slot, mesa): equipo
    reservas = dict()

    # Limitar el número de slots que se muestrana las numslots primeros
    if numslots > 0:
        slots = slots[:numslots]

    if salaobj.exists():
        nombresala = salaobj.first().nombre
        reservaobj = Reserva.objects.filter(mesa__sala=salaobj.first())
        for i in reservaobj:
            if i.slot.id not in reservas:
                reservas[i.slot.id] = dict()
            reservas[i.slot.id][i.mesa.id] = i.equipo.idequipo
        mesas = Mesa.objects.filter(sala=salaobj.first()).order_by("nombre")
    else:
        nombresala = 'PIT'
        reservaobj = Reserva.objects.all()
        for i in reservaobj:
            if i.slot.id not in reservas:
                reservas[i.slot.id] = dict()
            reservas[i.slot.id][i.mesa.id] = i.equipo.idequipo

        mesas = Mesa.objects.all().order_by("nombre")

    return mesas, slots, reservas, nombresala

@never_cache
def horario(request, sala):
    template = loader.get_template('pit/horario.html')

    # Se limita a 9 el máximo de registros a pintar
    mesas, slots, reservas, nombresala =_tabla_horario_futuro(sala, 9)

    context = {
        'mesas': mesas,
        'slots': slots,
        'reservas': reservas,
        'fechahoraactual': datetime.now(),
        'anchocol': str(75/len(mesas)).replace(',', '.'), #el 75 es porcentaje, la primera columna es 25 porque se establece en el html y el 75 porciento restante se reparte entre las demás
        'nombresala': nombresala
    }

    return HttpResponse(template.render(context, request))

@never_cache
def horario_1080(request, sala):
    template = loader.get_template('pit/horario1080.html')

    # Se limita a 9 el máximo de registros a pintar
    mesas, slots, reservas, nombresala =_tabla_horario_futuro(sala, 11)

    context = {
        'mesas': mesas,
        'slots': slots,
        'reservas': reservas,
        'fechahoraactual': datetime.now(),
        'anchocol': str(85/len(mesas)).replace(',', '.'), #el 85 es porcentaje, la primera columna es 15 porque se establece en el html y el 85 porciento restante se reparte entre las demás
        'nombresala': nombresala
    }

    return HttpResponse(template.render(context, request))

@never_cache
def horario_static(request, sala):
    template = loader.get_template('pit/horariostatic.html')

    # Se limita a 9 el máximo de registros a pintar
    mesas, slots, reservas, nombresala =_tabla_horario_futuro(sala, 0)

    context = {
        'mesas': mesas,
        'slots': slots,
        'reservas': reservas,
        'fechahoraactual': datetime.now(),
        'anchocol': str(85/len(mesas)).replace(',', '.'), #el 85 es porcentaje, la primera columna es 15 porque se establece en el html y el 85 porciento restante se reparte entre las demás
        'nombresala': nombresala,
        'salas': Sala.objects.all()
    }

    return HttpResponse(template.render(context, request))

def horario_futuro_completo(request, sala):
    template = loader.get_template('pit/horariofuturocompleto.html')

    # No se limita el máximo de registros a pintar
    mesas, slots, reservas, nombresala =_tabla_horario_futuro(sala, 0)

    context = {
        'mesas': mesas,
        'slots': slots,
        'reservas': reservas,
        'fechahoraactual': datetime.now(),
        'anchocol': str(75/len(mesas)).replace(',', '.'), #el 75 es porcentaje, la primera columna es 25 porque se establece en el html y el 75 porciento restante se reparte entre las demás
        'nombresala': nombresala
    }

    return HttpResponse(template.render(context, request))

def horario_pasado(request, sala):
    template = loader.get_template('pit/horariopasado.html')

    # No se limita el máximo de registros a pintar
    mesas, slots, reservas, nombresala =_tabla_horario_futuro(sala, 0, 1)

    context = {
        'mesas': mesas,
        'slots': slots,
        'reservas': reservas,
        'fechahoraactual': datetime.now(),
        'anchocol': str(75/len(mesas)).replace(',', '.'), #el 75 es porcentaje, la primera columna es 25 porque se establece en el html y el 75 porciento restante se reparte entre las demás
        'nombresala': nombresala
    }

    return HttpResponse(template.render(context, request))

def actualizar_horario(request):
    if request.method == 'GET':
        return HttpResponse(status=405)

    if request.method == 'POST':
        # Comprobar y leer campos de entrada
        if not all(x in request.POST for x in ['mesa', 'slot', 'equipo']):
            messages.error(request, "Falta campo en el formulario")
        mesa = int(request.POST['mesa'])
        slot = int(request.POST['slot'])
        equipo = int(request.POST['equipo'])

        # Obtener la info de base de datos
        mesaobj = Mesa.objects.filter(pk=mesa)
        slotobj = Slot.objects.filter(pk=slot)
        reserva_actual = Reserva.objects.filter(mesa=mesa, slot=slot)

        # Liberar slot
        if equipo == -1:
            if reserva_actual.exists():
                mensaje = 'Se va a liberar el slot {} de la mesa {}, actualmente asignado al equipo "{}".'.format(slotobj.first(), mesaobj.first(), reserva_actual.first().equipo)
            else:
                mensaje = ''
                messages.info(request, 'El slot {} de la mesa {} está libre actualmente, no hay nada que cambiar nada.'.format(slotobj.first(), mesaobj.first()))
        # Asignar equipo
        else:
            pequipoobj = Equipo.objects.filter(pk=equipo).first()

            aviso_previo = ''

            # Sala no preferida
            if pequipoobj.salapreferible.id != mesaobj.first().sala.id:
                aviso_previo += ' Ojo: No se espera que el equipo reserve en esta sala, deberia reservar en {}.'.format(pequipoobj.salapreferible.nombre)

            # Ya hay slot reservado
            reserva_futura = Reserva.objects.filter(equipo=equipo, slot__horainicio__gt=datetime.now())
            if reserva_futura.exists():
                aviso_previo += ' OjO: El equipo ya tiene reserva en el slot {} de la mesa {}.'.format(reserva_futura.first().slot, reserva_futura.first().mesa)

            # El slot ya estaba ocupado
            if reserva_actual.exists():
                if pequipoobj.id == reserva_actual.first().equipo.id:
                    mensaje = ''
                    messages.info(request, 'El slot {} de la mesa {} ya estaba asignado al equipo "{}", no hay que cambiar nada.'.format(slotobj.first(), mesaobj.first(), pequipoobj))
                else:
                    mensaje = 'Slot {} de la mesa {} actualmente asignado al equipo "{}", se va a reasignar al equipo "{}"'.format(reserva_actual.first(), reserva_actual.first().mesa, reserva_actual.first().equipo, pequipoobj)
            else:
                mensaje = 'Se va a asignar el slot {} de la mesa {} al equipo "{}"'.format(slotobj.first(), mesaobj.first(), pequipoobj)

        template = loader.get_template('pit/actualizarhorario.html')
        context = {
            'mesa': mesa,
            'slot': slot,
            'equipo': equipo,
            'mensaje': mensaje,
            'aviso_previo': aviso_previo
        }
        if mensaje == '':
            #Caso redundante, no hay nada que hacer
            return HttpResponseRedirect(reverse('pit:index'))
        else:
            return HttpResponse(template.render(context, request))

def confirmar_horario(request):
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
