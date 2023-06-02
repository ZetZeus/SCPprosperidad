from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("Cepillado",views.cepilladoInfo),
    path("Trozado",views.trozadoInfo),
    path("Secado",views.secadoInfo),
    path("Finger",views.fingerInfo),
    path("Moldurera",views.moldureraInfo),
    path("SalidaAserradero",views.aserraderoInfo)
]