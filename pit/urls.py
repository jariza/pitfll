from django.urls import path

from . import views

app_name = 'pit'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('horario/<int:sala>/', views.horario, name='horario'),
    path('actualizarhorario/', views.actualizar_horario, name='actualizarhorario'),
    path('confirmarhorario/', views.confirmar_horario, name='confirmarhorario'),
    path('horariocompleto/<int:sala>/', views.horario_futuro_completo, name='horariocompleto'),
    path('horariopasado/<int:sala>/', views.horario_pasado, name='horariopasado')
]