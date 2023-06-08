from django import forms
from .models import Area, Centrotrabajo,Maquina,Maderas,Proceso

class aserradero(forms.ModelForm):
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
                  'piezassalida',
                  'volumensalida',
                  'volumentotal']
class secado(forms.ModelForm):
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
                  'volumentotal']
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
                  'codigo_madera_ant',
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
                  'volumentotal']
        
class trozado(forms.ModelForm):
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
                  'volumentotal']
class finger(forms.ModelForm):
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
                  'piezascalidad',
                  'volumenentrada',
                  'volumencalidad',
                  'piezasreproceso',
                  'volumenreproceso',
                  'volumentotal']

class moldurera(forms.ModelForm):
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
                  'piezascalidad',
                  'volumenentrada',
                  'volumencalidad',
                  'piezasrechazoproc',
                  'volumenrechazoproc',
                  'volumentotal']
class reproceso(forms.ModelForm):
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
                  'piezassalida',
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

