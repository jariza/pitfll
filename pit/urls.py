from django.urls import path

from . import views

app_name = 'pit'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('horario/<int:sala>/', views.horario, name='horario'),
    path('actualizarhorario/', views.actualizarhorario, name='actualizarhorario'),
    path('confirmarhorario/', views.confirmarhorario, name='confirmarhorario'),
]