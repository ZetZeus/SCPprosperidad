from django.shortcuts import render
from django.db.models import Max
from django.contrib import messages
from django.db import connection

# Create your views here.
from django.http import HttpResponse
from .models import Centrotrabajo,Area, Maquina, Maderas, Proceso
from .forms import aserradero,secado,cepillado,trozado,finger,moldurera,reproceso, nuevaMadera



def home(request):
    info_area = Centrotrabajo.objects.all
    return render(request, 'homeRema.html',{'todo': info_area})

def actualizarMadera():
    with connection.cursor() as cursor:
        cursor.execute("""
        UPDATE "Maderas"
SET "volumenxPieza" = ("espesor"*"ancho"*"largo")/1000000, "factor" = 1/"cantidadxPaquete", "paquetes" = "piezas"/"cantidadxPaquete"
""")
        cursor.execute("""
        UPDATE "Maderas"
SET "volumenTotal" = "volumenxPieza"*"piezas"
        """)
        cursor.execute("""
        UPDATE "Maderas" SET "volumenreproceso" = "volumenxPieza" * "reproceso"
        """)


def nuevoCodigo(request):
    info_maderas = Maderas.objects.all
    info_ct = Centrotrabajo.objects.all
    p = Maderas.objects.aggregate(Max('id_madera')).get('id_madera__max')
    if request.method == "POST":
        form = nuevaMadera(request.POST or None)
        update_data = request.POST.copy()
        idMadera = p+1
        update_data.update({'id_madera': idMadera,
                            'id_centrotrabajo':'0',
                            'volumenxpieza':'0',
                            'factor':'0',
                            'volumentotal':'0',
                            'piezas':'0',
                            'paquetes':'0',
                            'reproceso':'0',
                            'volumenreproceso':'0'})
        nuevo_form = nuevaMadera(update_data)
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_madera = p+1

            for j in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera" FROM "Maderas"
                """
            ):
                if(j.codigo_madera == instance.codigo_madera):
                    messages.success(request,("Error ese nombre de codigo ya existe"))
                    return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})
            

            for i in Centrotrabajo.objects.raw(
                """
                SELECT "id_centroTrabajo", "nombre_centroTrabajo" FROM "CentroTrabajo"
                
                """
            ):
                if (i.nombre_centrotrabajo == instance.nombre_centrotrabajo):
                    instance.id_centrotrabajo = i.id_centrotrabajo
     
            

                
            instance.save()
            actualizarMadera()

        else:
            messages.success(request,("Error al ingresar"))
            return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})
                
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
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = aserradero(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumentotal':'0'})
        nuevo_form = aserradero(update_data)

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 2
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
                if (instance.piezasentrada != None):
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                
                instance.volumentotal = instance.volumenentrada

            instance.id_area = 1
            instance.id_centrotrabajo = 2

            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Aserradero'
                """
            ):
                    if (i.nombremaquina == instance.nombre_maquina):
                        instance.nombre_centrotrabajo = i.centrotrabajomaquina
                        instance.id_maquina = i.id_maquina
            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera))  
            actualizarMadera()
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
    
    else:
        return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

def secadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = secado(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumensalida': '0',
                            'volumentotal':'0',})
        nuevo_form = secado(update_data)

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 3
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
                if (instance.piezasentrada != None):
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000

                if(instance.piezassalida != None):    
                    instance.volumensalida = ((i.espesor * i.ancho * i.largo) * instance.piezassalida) / 1000000

                instance.volumentotal = instance.volumensalida

                instance.id_area = 1
                instance.id_centrotrabajo = 3

                for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Secado'
                """
            ):
                    if (i.nombremaquina == instance.nombre_maquina):
                        instance.nombre_centrotrabajo = i.centrotrabajomaquina
                        instance.id_maquina = i.id_maquina
                instance.save()
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))

                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
                """,(instance.piezasentrada,instance.codigo_madera_ant))
                
                
                connection.cursor().execute("""
                    UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s"""
                                   ,(instance.codigo_madera,)) 
                actualizarMadera() 
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        

        
        return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
    


    else:
        return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})


def cepilladoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = cepillado(request.POST or None)
        update_data = request.POST.copy()

        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumensalida': '0',
                            'volumenrechazohum': '0',
                            'volumenrechazodef': '0',
                            'volumenrechazoproc': '0',
                            'volumentotal':'0',
                            })
        nuevo_form = cepillado(update_data)
        
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
           

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
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,)) 

            actualizarMadera() 
        else:
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
        form = trozado(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumensalida': '0',
                            'volumentotal':'0',})
        nuevo_form = trozado(update_data)
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
            instance.codigo_madera_ant = update_data['codigo_madera_ant']

            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 5
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

                if(instance.piezasentrada != None):    
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                if(instance.piezassalida != None):
                    instance.volumensalida = ((i.espesor * i.ancho * i.largo) * instance.piezassalida) / 1000000

                instance.volumentotal = instance.volumensalida
                

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
            

            instance.save()

            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            
            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,))

            actualizarMadera() 
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})


def fingerInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = finger(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumencalidad': '0',
                            'volumentotal':'0',
                            'volumenreproceso': '0',
                            })
        nuevo_form = finger(update_data)
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 6
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                if(instance.piezasentrada != None):
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                if(instance.piezascalidad != None):
                    instance.volumencalidad = ((i.espesor * i.ancho * i.largo) * instance.piezascalidad) / 1000000
                if(instance.piezasreproceso != None):
                    instance.volumenreproceso = ((i.espesor * i.ancho * i.largo) * instance.piezasreproceso) / 1000000

                instance.volumentotal = instance.volumencalidad + instance.volumenreproceso


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

            instance.save()

            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezascalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
        
            connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" + %s WHERE "codigo_madera" = %s
                """,(instance.piezasreproceso, instance.codigo_madera)) 

            actualizarMadera() 
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
   
        return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})


def moldureraInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = moldurera(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumencalidad': '0',
                            'volumentotal':'0',
                            'volumenrechazoproc': '0',
                            })
        nuevo_form = moldurera(update_data)
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 8
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

                if (instance.piezasentrada != None):    
                    instance.volumenentrada = ((i.espesor * i.ancho * i.largo) * instance.piezasentrada) / 1000000
                    
                if(instance.piezascalidad != None):    
                    instance.volumencalidad = ((i.espesor * i.ancho * i.largo) * instance.piezascalidad) / 1000000
                    
                if (instance.piezasrechazoproc != None):    
                    instance.volumenrechazoproc = ((i.espesor * i.ancho * i.largo) * instance.piezasrechazoproc) / 1000000

                instance.volumentotal = instance.volumencalidad + instance.volumenrechazoproc


            instance.id_area = 1
            instance.id_centrotrabajo = 8
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Moldurera'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina
            
            instance.save()
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezascalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s
                """,(instance.codigo_madera,)) 

            actualizarMadera()   
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
 
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})


def reprocesoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = reproceso(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida':'0',
                            'volumentotal':'0'})
        nuevo_form = reproceso(update_data)
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 8
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
                if(instance.piezassalida != None):
                    instance.volumensalida = ((i.espesor * i.ancho * i.largo) * instance.piezassalida) / 1000000

                instance.volumentotal = instance.volumensalida
            instance.id_area = 1
            instance.id_centrotrabajo = 7
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Reproceso'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina

            instance.save()
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas}) 
        return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
    else:
        return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    