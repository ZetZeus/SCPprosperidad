from django.shortcuts import render
from django.db.models import Max
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse
from .models import Centrotrabajo,Area, Maquina, Maderas, Proceso
from .forms import cepillado, nuevaMadera



def home(request):
    info_area = Centrotrabajo.objects.all
    return render(request, 'homeRema.html',{'todo': info_area})

def nuevoCodigo(request):
    info_maderas = Maderas.objects.all
    info_ct = Centrotrabajo.objects.all
    p = Proceso.objects.aggregate(Max('id_madera')).get('id_madera__max')
    if request.method == "POST":
        form = nuevaMadera(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id_madera = p+1
            print('comprobando si el form es valido')

            for i in Centrotrabajo.objects.raw(
                """
                SELECT "id_centroTrabajo", "nombre_centroTrabajo" FROM "CentroTrabajo"
                
                """
            ):
                print(i.nombre_centroTrabajo, instance.centroTrabajo)
                
                if (i.nombre_centroTrabajo == instance.centroTrabajo):
                    print('nombres despues del if',i.nombre_centrotrabajo, instance.centroTrabajo)
                    instance.id_centrotrabajo = i.id_centrotrabajo
                
            instance.save()    
        return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})

    else:
        return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})
    
    

def entradaAserraderoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

def aserraderoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

def secadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

def cepilladoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = cepillado(request.POST or None)
        update_data = request.POST.copy()

        idProceso = p+1
        """update_data.update({'piezascalidad': '0',
                            'piezasreproceso':'0',
                            'volumenreproceso':'0',
                            'volumencalidad':'0',
                            })
        nuevo_form = cepillado(update_data)
        print(nuevo_form.data)
        print('\n')
        print(nuevo_form.cleaned_data)"""
        if form.is_valid():
            print('entrando a validar')
            instance = form.save(commit=False)
            instance.id_proceso = p+1
            """instance.piezasreproceso = 0
            instance.volumenreproceso = 0
            instance.volumencalidad = 0
            instance.piezascalidad = 0"""


            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 4
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
                if (instance.piezasentrada != None):
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000

                if(instance.piezassalida != None):    
                    instance.volumensalida = ((i.espesor * i.ancho * i.largo) * instance.piezassalida) / 1000000
                if(instance.piezasrechazohum != None):
                    instance.volumenrechazohum = ((i.espesor * i.ancho * i.largo) * instance.piezasrechazohum) / 1000000

                if(instance.piezasrechazodef != None):
                    instance.volumenrechazodef = ((i.espesor * i.ancho * i.largo) * instance.piezasrechazodef) / 1000000
                
                if(instance.piezasrechazoproc != None):
                    instance.volumenrechazoproc = ((i.espesor * i.ancho * i.largo) * instance.piezasrechazoproc) / 1000000

                instance.volumentotal = instance.volumensalida

            instance.id_area = 1
            instance.id_centrotrabajo = 4
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Cepillado'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina
            
            instance.save()
        else:
            print('el formulario no es valido')
            messages.success(request, ('Error al ingresar'))
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        

        
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
    


    else:
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})


def trozadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = cepillado(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id_proceso = p+1
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 5
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                    instance.volumensalida = ((i.espesor * i.ancho * i.largo) * instance.piezassalida) / 1000000

                

            instance.id_area = 1
            instance.id_centrotrabajo = 5
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Trozado'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina
            

            instance.volumentotal = instance.volumensalida
                
            instance.save()    
        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

def fingerInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = cepillado(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id_proceso = p+1
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 6
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                    instance.volumencalidad = ((i.espesor * i.ancho * i.largo) * instance.piezascalidad) / 1000000
                    instance.volumenreproceso = ((i.espesor * i.ancho * i.largo) * instance.piezasreproceso) / 1000000

                

            instance.id_area = 1
            instance.id_centrotrabajo = 6
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Finger'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina
            

            instance.volumentotal = instance.volumencalidad + instance.volumenreproceso
                
            instance.save()    
        return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

def moldureraInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = cepillado(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id_proceso = p+1
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 7
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                    instance.volumencalidad = ((i.espesor * i.ancho * i.largo) * instance.piezascalidad) / 1000000
                    instance.volumenrechazoproc = ((i.espesor * i.ancho * i.largo) * instance.piezasrechazoproc) / 1000000

                

            instance.id_area = 1
            instance.id_centrotrabajo = 7
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Moldurera'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina
            

            instance.volumentotal = instance.volumencalidad + instance.volumenrechazoproc
                
            instance.save()    
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

 