from django import forms
from .models import Area, Centrotrabajo,Maquina,Maderas,Proceso

class cepillado(forms.ModelForm):

    class Meta:
        model = Proceso
        fields = ['id_proceso',
                  'fecha',
                  'nombre_maquina',
                  'codigo_madera',
                  'piezasentrada',
                  'piezassalida',
                  'piezasrechazohum',
                  'piezasrechazodef',
                  'piezasrechazoproc']
    
