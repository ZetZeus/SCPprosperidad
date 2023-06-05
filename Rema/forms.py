from django import forms
from .models import Area, Centrotrabajo,Maquina,Maderas,Proceso

class cepillado(forms.ModelForm):

    class Meta:
        model = Proceso
        fields = ['id_proceso',
                  'id_madera',
                  'id_area',
                  'id_centrotrabajo',
                  'id_maquina',
                  'fecha',
                  'nombre_maquina',
                  'codigo_madera',
                  'piezasentrada',
                  'piezassalida',
                  'volumenentrada',
                  'volumensalida',
                  'piezasrechazohum',
                  'piezasrechazodef',
                  'piezasrechazoproc',
                  'volumenrechazohum',
                  'volumenrechazodef',
                  'volumenrechazoproc',
                  'piezasreproceso',
                  'volumenreproceso',
                  'piezascalidad',
                  'volumencalidad',
                  'volumentotal']

