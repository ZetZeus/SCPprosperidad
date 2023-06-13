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
                  'piezassalida',
                  'volumensalida',
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
                  'piezassalida',
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
                  'piezasentrada',
                  'piezassalida',
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
                  'piezasentrada',
                  'piezassalida',
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
                  'piezasentrada',
                  'piezascalidad',
                  'volumenentrada',
                  'volumencalidad',
                  'piezasreproceso',
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
                  'piezasentrada',
                  'piezascalidad',
                  'volumenentrada',
                  'volumencalidad',
                  'piezasrechazoproc',
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

