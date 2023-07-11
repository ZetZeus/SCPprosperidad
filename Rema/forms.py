from django import forms
from .models import Area, Centrotrabajo,Maquina,Maderas,Proceso

class entradaAserraderoForm(forms.ModelForm):
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
                  'piezasease',
                  'volumenease',
                  'volumentotal']

class aserraderoForm(forms.ModelForm):
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
                  'codigo_madera_ant',
                  'volumenentrada',
                  'volumensalida',
                  'volumentotal']
class secadoForm(forms.ModelForm):
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
                  'codigo_madera_ant',
                  'volumenentrada',
                  'volumensalida',
                  'volumentotal']
class cepilladoForm(forms.ModelForm):

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
                  'codigo_madera_ant',
                  'volumenentrada',
                  'volumensalida',
                  'volumenrechazohum',
                  'volumenrechazodef',
                  'volumenrechazoproc',
                  'volumentotal']
        
class trozadoForm(forms.ModelForm):
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
                  'codigo_madera_ant',

                  'volumenentrada',
                  'volumensalida',
                  'volumentotal']
class fingerForm(forms.ModelForm):
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
                  'codigo_madera_ant',
                  'volumenentrada',
                  'volumencalidad',
                  'volumenreproceso',
                  'volumentotal']

class moldureraForm(forms.ModelForm):
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
                  'codigo_madera_ant',
                  'volumenentrada',
                  'volumencalidad',
                  'volumenrechazoproc',
                  'volumentotal']
class reprocesoForm(forms.ModelForm):
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
                  'codigo_madera_ant',
                  'volumensalida',
                  'volumentotal']        

class nuevaMadera(forms.ModelForm):
    class Meta:
        model = Maderas
        fields =['id_madera',
                 'id_centrotrabajo',
                 'nombre_centrotrabajo',
                 'codigo_madera',
                 'espesor',
                 'ancho',
                 'largo',
                 'diametro',
                 'volumenxpieza',
                 'cantidadxpaquete',
                 'factor',
                 'piezas',
                 'volumentotal',
                 'paquetes',
                 'reproceso',
                 'volumenreproceso']

