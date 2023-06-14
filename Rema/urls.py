from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("Cepillado",views.cepilladoInfo),
    path("Trozado",views.trozadoInfo),
    path("Secado",views.secadoInfo),
    path("Finger",views.fingerInfo),
    path("Moldurera",views.moldureraInfo),
    path("SalidaAserradero",views.aserraderoInfo),
    path("EntradaAserradero",views.entradaAserraderoInfo),
    path("nuevocodigo",views.nuevoCodigo),
    path("Reproceso", views.reprocesoInfo),
    path("SalidaAserradero/",views.AserraderoFormView.as_view(),name='salida_aserradero'),
    path("SalidaAserradero/preview",views.previsualizacion,name='previsualizacion'),
    path("Cepillado/",views.CepilladoFormView.as_view(),name='cepillado'),
    path("Cepillado/preview",views.previsualizacionCep,name='previsualCep')
]