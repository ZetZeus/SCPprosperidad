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
    path("Cepillado/preview",views.previsualizacionCep,name='previsualCep'),
    path("Secado/",views.SecadoFormView.as_view(),name='secado'),
    path("Secado/previsualizacionSec",views.previsualizacionSec,name='previsualSec'),
    path("Trozado/",views.TrozadoFormView.as_view(),name='trozado'),
    path("Trozado/previsualizacionTRZ",views.previsualizacionTRZ,name='previsualTRZ'),
    path("Finger/",views.FingerFormView.as_view(),name='finger'),
    path("Finger/previsualizacionFNG",views.previsualizacionFNG,name='previsualFNG'),
    path("Moldurera/",views.MoldureraFormView.as_view(),name='moldurera'),
    path("Moldurera/previsualizacionMOL",views.previsualizacionMOL,name='previsualMOL')
]