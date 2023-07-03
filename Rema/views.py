from django.shortcuts import render, redirect
from django.db.models import Max
from django.contrib import messages
from django.http import HttpResponse
from django.db import connection
from formtools.preview import FormPreview
from formtools.wizard.views import SessionWizardView
from django.views.generic.edit import FormView
from django.core.cache import cache



# Create your views here.
from .models import Centrotrabajo,Area, Maquina, Maderas, Proceso
from .forms import entradaAserraderoForm,aserraderoForm,secadoForm,cepilladoForm,trozadoForm,fingerForm,moldureraForm,reprocesoForm, nuevaMadera



def home(request):
    info_area = Centrotrabajo.objects.all
    return render(request, 'homeRema.html',{'todo': info_area})

def error404(request,exception):
    return render(request, '404.html')

def actualizarMadera():
    with connection.cursor() as cursor:
        cursor.execute("""
        UPDATE "Maderas"
        SET "volumenxPieza" = ("espesor"*"ancho"*"largo")/1000000, "factor" = 1/"cantidadxPaquete", "paquetes" = "piezas"/"cantidadxPaquete"
        """)
        connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenxPieza" = ("diametro" * "diametro" * "largo") /10000 WHERE "codigo_madera" LIKE 'EASE%'
            """)
        cursor.execute("""
        UPDATE "Maderas"
        SET "volumenTotal" = "volumenxPieza"*"piezas"
        """)
        cursor.execute("""
        UPDATE "Maderas" SET "volumenreproceso" = "volumenxPieza" * "reproceso"
        """)
        cursor.execute("""
        UPDATE "Maderas" SET "volumen_trz-a" = "volumenxPieza" * "piezas_trz-a"
        """)
        cursor.execute("""
        UPDATE "Maderas" SET "volumen_trz-b" = "volumenxPieza" * "piezas_trz-b"
        """)
        cursor.execute("""
        UPDATE "Maderas" SET "volumen_trz-c" = "volumenxPieza" * "piezas_trz-c"
        """)
        cursor.execute("""
        UPDATE "Maderas" SET "volumen_trz-d" = "volumenxPieza" * "piezas_trz-d"
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
        espesor = request.POST.get('espesor')
        ancho = request.POST.get('ancho')
        largo = request.POST.get('largo')
        diametro = request.POST.get('diametro')
        cantidadxpaquete = request.POST.get('cantidadxpaquete')
        if espesor == '' or ancho == '' or largo == '' or diametro == '' or cantidadxpaquete == '':
            messages.error(request,'Asegurese de llenar todos los campos de texto')
            return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})
        
        if float(espesor) < 0 or float(ancho) < 0 or float(largo) < 0 or float(diametro) < 0 or float(cantidadxpaquete) < 0:
            messages.error(request,'Medidas inválidas (menor a cero)')
            return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})



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
     
            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-a" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-b" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-c" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-d" = 0 WHERE "codigo_madera" = %s
            """,(instance.codigo_madera,))

                
            instance.save()
            actualizarMadera()

        else:
            messages.success(request,("Error al ingresar"))
            return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})
                
        return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})

    else:
        return render(request,'nuevoCodigoForm.html', {'inf_madera': info_maderas, 'inf_ct':info_ct})

def calcularVolumenEASE(codigo_de_madera, piezas_recibidas):
    madera = Maderas.objects.get(codigo_madera = codigo_de_madera)
    volumen = (madera.diametro * madera.diametro * madera.largo * piezas_recibidas) / 10000
    return volumen

def calcularVolumen(codigo_de_madera, piezas_recibidas):
    madera = Maderas.objects.get(codigo_madera = codigo_de_madera)
    volumen = ((madera.espesor)* (madera.ancho) * (madera.largo) * int(piezas_recibidas)) / 1000000    
    return volumen

class EntradaASEFormView(FormView):
    template_name = 'entradaAseForm.html'
    form_class = entradaAserraderoForm
    success_url = '/Rema/EntradaAserradero'

    def form_valid(self, form):
        form_data = form.cleaned_data
        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionEASE')
        return super().form_valid(form)
    
def previsualizacionEASE(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == "POST":
        form = entradaAserraderoForm(request.POST or None)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')    
        idProceso = p+1
        update_data.update({'idproceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida':'0',
                            'volumentotal':'0'})
        nuevo_formVis = entradaAserraderoForm(update_data)
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(piezas_salida) < 0: 
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')

            id_madera = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 1"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            form_data['id_madera'] = id_madera    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 1

            volumendSalida = calcularVolumenEASE(codigo_madera,piezas_salida)
            form_data['volumensalida'] = volumendSalida
            form_data['volumentotal'] = volumendSalida

            cache.delete('form_data')
            return render(request, 'previsualEASE.html',{'form_data': form_data, 'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = entradaAserraderoForm(form_data) if form_data else entradaAserraderoForm()
    return render(request,'entradaAseForm.html',{'form':form,'maquinas':info_maquinas,'maderas':info_maderas})    
    

def entradaAserraderoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'idproceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida':'0',
                            'volumentotal':'0'})
        nuevo_form = entradaAserraderoForm(update_data)
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_salida) < 0: 
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "diametro","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 1
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

                if(instance.piezassalida != None):    
                    instance.volumensalida = (i.diametro * i.diametro * i.largo * instance.piezassalida) / 10000

                instance.volumentotal = instance.volumensalida

                instance.id_area = 1
                instance.id_centrotrabajo = 1
                instance.nombre_centrotrabajo = 'EntradaAserradero'
            instance.save()
            
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))
            
            actualizarMadera()
            
            cache.delete('form_data')
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = entradaAserraderoForm(form_data)
        return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'form':form_data})

class AserraderoFormView(FormView):
    template_name = 'salidaAseForm.html'
    form_class = aserraderoForm
    success_url = '/Rema/SalidaAserradero'

    def form_valid(self, form):
        form_data = form.cleaned_data

        if 'ingresar' in self.request.POST:

            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacion')
        return super().form_valid(form)
def previsualizacion(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == 'POST':
        form = aserraderoForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida': '0',
                            'volumenentrada': '0',
                            'volumentotal':'0'})
        nuevo_formVis = aserraderoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '' or piezas_entrada == '':
            messages.error(request, 'No se puede previsualizar sin piezas ingresadas')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0:
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        
        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese la Fecha correctamente')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})


        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')
            codigo_madera_ant = request.POST.get('codigo_madera_ant')
            id_madera = None
            id_maquina = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 2"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Aserradero'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i.id_maquina
                    break
            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 2
            form_data['piezasentrada'] = piezas_entrada
            volumenEntrada = calcularVolumenEASE(codigo_madera_ant,piezas_entrada)    
            volumen = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumensalida'] = volumen
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumentotal'] = volumen
            print(volumenEntrada)

            cache.delete('form_data')
            return render(request, 'previsualizacion.html', {'form_data': form_data, 'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = aserraderoForm()
    
    return render(request,'salidaAseForm.html',{'form':form,'maquinas':info_maquinas,'maderas':info_maderas}) 


def aserraderoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada':'0',
                            'volumensalida': '0',
                            'volumentotal':'0'})
        nuevo_form = aserraderoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '' or piezas_entrada == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese la Fecha correctamente')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 2
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
            instance.piezasentrada = float(piezas_entrada)
            print(type(instance.codigo_madera_ant),type(instance.piezasentrada))

            print(instance.codigo_madera_ant, instance.piezasentrada)
            volumen = calcularVolumen(instance.codigo_madera,instance.piezassalida)
            volumenEntrada = calcularVolumenEASE(instance.codigo_madera_ant,instance.piezasentrada)
            instance.volumensalida = volumen
            instance.volumenentrada = volumenEntrada
            instance.volumentotal = volumen

            instance.id_area = 1
            instance.id_centrotrabajo = 2
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'SalidaAserradero'
                """
            ):
                    if (i.nombremaquina == instance.nombre_maquina):
                        instance.nombre_centrotrabajo = i.centrotrabajomaquina
                        instance.id_maquina = i.id_maquina

            if instance.piezasentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas, 'nuevo_form':nuevo_form})            
            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada, instance.codigo_madera_ant))
            actualizarMadera()
            cache.delete('form_data')
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
    
    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = aserraderoForm(form_data)
        return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'form':form_data})


class SecadoFormView(FormView):
    template_name = 'secadoForm.html'
    form_class = secadoForm
    success_url = '/Rema/Secado'

    def form_valid(self,form):
        form_data = form.cleaned_data
        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionSec')
        return super().form_valid(form)
def previsualizacionSec(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == 'POST':
        form = secadoForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumensalida': '0',
                            'volumentotal':'0'})
        nuevo_formVis = secadoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')

        if piezas_entrada == '' or piezas_salida == '':
            messages.error(request, 'No se puede previsualizar sin piezas ingresadas')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(piezas_salida) > float(piezas_entrada):
            messages.error(request, 'Piezas de salida no puede ser mayor a la entrada')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')
            codigo_madera_ant = request.POST.get('codigo_madera_ant')
            id_madera = None
            id_maquina = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 3"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Secado'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i.id_maquina
                    break
            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 3
            volumenEntrada = calcularVolumen(codigo_madera_ant,piezas_entrada)
            volumenSalida = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumensalida'] = volumenSalida
            form_data['piezasentrada'] = piezas_entrada
            cache.delete('form_data')

            return render(request,'previsualSec.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = secadoForm(form_data) if form_data else secadoForm()
    return render(request,'secadoForm.html',{'form':form,'maquinas':info_maquinas,'maderas':info_maderas})    

def secadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
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
        nuevo_form = secadoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')

        if piezas_entrada == '' or piezas_salida == '':
            messages.error(request, 'No se puede Ingresar sin agregar todas las piezas')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_salida) > float(piezas_entrada):
            messages.error(request,'Piezas salida no puede ser mayor a la entrada')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
 
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
            cantidad_disponibleCEP = madera_anterior.reproceso
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 3
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                

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

            instance.volumenentrada = calcularVolumen(instance.codigo_madera_ant,instance.piezasentrada)

            if instance.piezasentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
            if instance.codigo_madera_ant[0] == 'C':
                if instance.piezasentrada > cantidad_disponibleCEP:
                    messages.error(request, 'La cantidad de piezas de CEP ingresada es superior a la disponible')
                    return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})    
            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))
            if instance.codigo_madera_ant[0] != 'C':
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
                """,(instance.piezasentrada,instance.codigo_madera_ant))
            
            if instance.codigo_madera_ant[0] == 'C':
                connection.cursor().execute("""
                    UPDATE "Maderas"
                    SET "reproceso" = "reproceso" - %s
                    WHERE "codigo_madera" = %s
                    """,(instance.piezasentrada, instance.codigo_madera_ant))
                
            actualizarMadera()
            cache.delete('form_data')
                
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
   
        return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})

    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = secadoForm(form_data)
        return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas, 'form':form_data})

class CepilladoFormView(FormView):
    template_name = 'cepilladoForm.html'
    form_class = cepilladoForm
    success_url = '/Rema/Cepillado'

    def form_valid(self, form):
        form_data = form.cleaned_data

        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionCep')
        return super().form_valid(form)
    
def previsualizacionCep(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == 'POST':
        form = cepilladoForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
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
                            'volumentotal':'0',})
        nuevo_formVis = cepilladoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')
        piezas_rechazohum = request.POST.get('piezasrechazohum')
        piezas_rechazodef = request.POST.get('piezasrechazodef')
        piezas_rechazoproc = request.POST.get('piezasrechazoproc')
        suma_salida = float(piezas_salida) + float(piezas_rechazodef) + float(piezas_rechazohum) + float(piezas_rechazoproc)
        if piezas_entrada == '' or piezas_salida == '' or piezas_rechazodef == '' or piezas_rechazohum == '' or piezas_rechazoproc == '':
                messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 or float(piezas_rechazodef) < 0 or float(piezas_rechazohum) < 0 or float(piezas_rechazoproc) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if suma_salida > float(piezas_entrada):
            messages.error(request,'Piezas salida y rechazos no pueden ser mayor a la entrada')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_salida = float(request.POST.get('piezassalida'))
            piezas_rechazohum = float(request.POST.get('piezasrechazohum'))
            piezas_rechazodef = float(request.POST.get('piezasrechazodef'))
            piezas_rechazoproc = float(request.POST.get('piezasrechazoproc'))

            codigo_madera = request.POST.get('codigo_madera')
            codigo_madera_ant = request.POST.get('codigo_madera_ant')
            id_madera = None
            id_maquina = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 4"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break
            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Cepillado'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i .id_maquina
                    break
            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 4

            
            volumenEntrada = calcularVolumen(codigo_madera_ant,piezas_entrada)
            volumenSalida = calcularVolumen(codigo_madera,piezas_salida)
            volumenRechazoHum = calcularVolumen(codigo_madera,piezas_rechazohum)
            volumenRechazoDef = calcularVolumen(codigo_madera,piezas_rechazodef)
            volumenRechazoProc = calcularVolumen(codigo_madera,piezas_rechazoproc)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumensalida'] = volumenSalida
            form_data['volumenrechazohum'] = volumenRechazoHum
            form_data['volumenrechazodef'] = volumenRechazoDef
            form_data['volumenrechazoproc'] = volumenRechazoProc

            cache.delete('form_data')
            return render(request,'previsualCep.html',{'form_data': form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = cepilladoForm(form_data) if form_data else cepilladoForm()
    return render(request,'cepilladoForm.html',{'form':form,'inf_maquinas':info_maquinas,'inf_maderas':info_maderas})

def cepilladoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
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
        nuevo_form = cepilladoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')
        piezas_rechazohum = request.POST.get('piezasrechazohum')
        piezas_rechazodef = request.POST.get('piezasrechazodef')
        piezas_rechazoproc = request.POST.get('piezasrechazoproc')
        suma_salida = float(piezas_salida) + float(piezas_rechazodef) + float(piezas_rechazohum) + float(piezas_rechazoproc)
        if piezas_entrada == '' or piezas_salida == '' or piezas_rechazodef == '' or piezas_rechazohum == '' or piezas_rechazoproc == '':
                messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if suma_salida > float(piezas_entrada):
            messages.error(request, 'Suma de piezas salida más rechazos no puede ser superior a entrada')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 or float(piezas_rechazodef) < 0 or float(piezas_rechazohum) < 0 or float(piezas_rechazoproc) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
           

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 4
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
                if (instance.piezasentrada != None):
                    instance.volumenentrada = calcularVolumen(instance.codigo_madera_ant,instance.piezasentrada)

                if(instance.piezassalida != None):    
                    instance.volumensalida = calcularVolumen(instance.codigo_madera,instance.piezassalida)
                if(instance.piezasrechazohum != None):
                    instance.volumenrechazohum = calcularVolumen(instance.codigo_madera,instance.piezasrechazohum)

                if(instance.piezasrechazodef != None):
                    instance.volumenrechazodef = calcularVolumen(instance.codigo_madera, instance.piezasrechazodef)
                
                if(instance.piezasrechazoproc != None):
                    instance.volumenrechazoproc = calcularVolumen(instance.codigo_madera,instance.piezasrechazoproc)

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
            
            if instance.piezasentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" + %s WHERE "codigo_madera" = %s
                """,(instance.piezasrechazohum, instance.codigo_madera)) 

            actualizarMadera() 
            cache.delete('form_data')
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
               
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = cepilladoForm(form_data)
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'form':form_data})

class TrozadoFormView(FormView):
    template_name = 'trozadoForm.html'
    form_class = trozadoForm
    success_url = '/Rema/Trozado'

    def form_valid(self, form):
        form_data = form.cleaned_data
        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionTRZ')
        return super().form_valid(form)

def previsualizacionTRZ(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == 'POST':
        form = trozadoForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumensalida': '0',
                            'volumentotal':'0',
                            'volumen_trz_a':'0',
                            'volumen_trz_b':'0',
                            'volumen_trz_c':'0',
                            'volumen_trz_d':'0',
                            'piezassalida':'0'})
        nuevo_formVis = trozadoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        #piezas_salida = request.POST.get('piezassalida')
        piezas_cat_a = request.POST.get('piezas_trz_a')
        piezas_cat_b = request.POST.get('piezas_trz_b')
        piezas_cat_c = request.POST.get('piezas_trz_c')
        piezas_cat_d = request.POST.get('piezas_trz_d')
        sumaCategorias = float(piezas_cat_a)+float(piezas_cat_b)+float(piezas_cat_c)+float(piezas_cat_d)
        if piezas_entrada == '' or piezas_cat_a == '' or piezas_cat_b=='' or piezas_cat_c == '' or piezas_cat_d=='':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_cat_a) < 0 or float(piezas_cat_b) < 0 or float(piezas_cat_c) < 0 or float(piezas_cat_d) < 0 or float(piezas_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if sumaCategorias > float(piezas_entrada):
            messages.error(request, 'Suma de las categorias no puede ser superior a entrada')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        #if float(piezas_salida) > float(piezas_entrada):
         #   messages.error(request, 'Piezas Salida no puede ser superior a entrada')
          #  return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
            
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            #piezas_salida = float(request.POST.get('piezassalida'))
            piezas_cat_a = request.POST.get('piezas_trz_a')
            piezas_cat_b = request.POST.get('piezas_trz_b')
            piezas_cat_c = request.POST.get('piezas_trz_c')
            piezas_cat_d = request.POST.get('piezas_trz_d')
            codigo_madera = request.POST.get('codigo_madera')
            codigo_madera_ant = request.POST.get('codigo_madera_ant')
            id_madera = None
            id_maquina = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 5"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Trozado'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i.id_maquina
                    break
            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 5 
            volumenEntrada = calcularVolumen(codigo_madera_ant,piezas_entrada)
            volumenSalida = calcularVolumen(codigo_madera,sumaCategorias)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumensalida'] = volumenSalida
            form_data['volumentotal'] = volumenSalida
            form_data['volumen_trz_a'] = calcularVolumen(codigo_madera,piezas_cat_a)
            form_data['volumen_trz_b'] = calcularVolumen(codigo_madera,piezas_cat_b)
            form_data['volumen_trz_c'] = calcularVolumen(codigo_madera,piezas_cat_c)
            form_data['volumen_trz_d'] = calcularVolumen(codigo_madera,piezas_cat_d)
            form_data['piezassalida'] = int(sumaCategorias)
            form_data['piezas_trz_a'] = int(piezas_cat_a)
            form_data['piezas_trz_b'] = int(piezas_cat_b)
            form_data['piezas_trz_c'] = int(piezas_cat_c)
            form_data['piezas_trz_d'] = int(piezas_cat_d)


            print(form_data)
            cache.delete('form_data')
            return render(request,'previsualTRZ.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = trozadoForm(form_data) if form_data else trozadoForm()
    return render(request,'trozadoForm.html',{'form':form,'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})



def trozadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumensalida': '0',
                            'volumentotal':'0',
                            'volumen_trz_a':'0',
                            'volumen_trz_b':'0',
                            'volumen_trz_c':'0',
                            'volumen_trz_d':'0',
                            'piezassalida':'0'})
        nuevo_form = trozadoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        #piezas_salida = request.POST.get('piezassalida')
        piezas_cat_a = request.POST.get('piezas_trz_a')
        piezas_cat_b = request.POST.get('piezas_trz_b')
        piezas_cat_c = request.POST.get('piezas_trz_c')
        piezas_cat_d = request.POST.get('piezas_trz_d')
        sumaCategorias = float(piezas_cat_a)+float(piezas_cat_b)+float(piezas_cat_c)+float(piezas_cat_d)

        if piezas_entrada == '' or piezas_cat_a == '' or piezas_cat_b == '' or piezas_cat_c == '' or piezas_cat_d == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})
        if float(piezas_cat_a) < 0 or float(piezas_cat_b) < 0 or float(piezas_cat_c) < 0 or float(piezas_cat_d) < 0 or float(piezas_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})
        if sumaCategorias > float(piezas_entrada):
            messages.error(request, 'Suma de las categorias no puede ser superior a entrada')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
          
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
            instance.codigo_madera_ant = update_data['codigo_madera_ant']

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 5
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

                if(instance.piezasentrada != None):    
                    instance.volumenentrada = calcularVolumen(instance.codigo_madera_ant,instance.piezasentrada)

            instance.volumensalida = calcularVolumen(instance.codigo_madera, sumaCategorias)
            instance.volumentotal = instance.volumensalida

            instance.volumen_trz_a = calcularVolumen(instance.codigo_madera,int(piezas_cat_a))
            instance.volumen_trz_b = calcularVolumen(instance.codigo_madera,int(piezas_cat_b))
            instance.volumen_trz_c = calcularVolumen(instance.codigo_madera,int(piezas_cat_c))
            instance.volumen_trz_d = calcularVolumen(instance.codigo_madera,int(piezas_cat_d))

            instance.piezas_trz_a = int(piezas_cat_a)
            instance.piezas_trz_b = int(piezas_cat_b)
            instance.piezas_trz_c = int(piezas_cat_c)
            instance.piezas_trz_d = int(piezas_cat_d)

            instance.piezassalida = sumaCategorias
                

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
            
            if instance.piezasentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})



            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-a" = "piezas_trz-a" + %s WHERE "codigo_madera" = %s
            """,(instance.piezas_trz_a, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-b" = "piezas_trz-b" + %s WHERE "codigo_madera" = %s
            """,(instance.piezas_trz_b, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-c" = "piezas_trz-c" + %s WHERE "codigo_madera" = %s
            """,(instance.piezas_trz_c, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-d" = "piezas_trz-d" + %s WHERE "codigo_madera" = %s
            """,(instance.piezas_trz_d, instance.codigo_madera))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = "reproceso" + %s + %s WHERE "codigo_madera" = %s
            """,(instance.piezas_trz_b,instance.piezas_trz_c,instance.codigo_madera))

            actualizarMadera() 
            cache.delete('form_data')
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = trozadoForm(form_data)
        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'form':form_data})


class FingerFormView(FormView):
    template_name = 'fingerForm.html'
    form_class = fingerForm
    success_url = '/Rema/Finger'

    def form_valid(self, form):
        form_data = form.cleaned_data
        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionFNG')
        return super().form_valid(form)
    
def previsualizacionFNG(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == 'POST':
        form = fingerForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumencalidad': '0',
                            'volumenreproceso':'0',
                            'volumentotal':'0'})
        nuevo_formVis = fingerForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_calidad = request.POST.get('piezascalidad')
        piezas_reproceso = request.POST.get('piezasreproceso')
        suma_salida = float(piezas_calidad) + float(piezas_reproceso)
        if piezas_entrada == '' or piezas_calidad == '' or piezas_reproceso == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_entrada) < 0 or float(piezas_calidad) < 0 or float(piezas_reproceso) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if suma_salida > float(piezas_entrada):
            messages.error(request,'Piezas calidad más reproceso no puede ser superior a entrada')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_calidad = float(request.POST.get('piezascalidad'))
            piezas_reproceso = float(request.POST.get('piezasreproceso'))
            codigo_madera = request.POST.get('codigo_madera')
            codigo_madera_ant = request.POST.get('codigo_madera_ant')
            id_madera = None
            id_maquina = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 6"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Trozado'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i.id_maquina
                    break
            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 6
            volumenEntrada = calcularVolumen(codigo_madera_ant,piezas_entrada)
            volumenCalidad = calcularVolumen(codigo_madera,piezas_calidad)
            volumenReproceso = calcularVolumen(codigo_madera, piezas_reproceso)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumencalidad'] = volumenCalidad
            form_data['volumenreproceso'] = volumenReproceso
            form_data['piezasentrada'] = piezas_entrada
            form_data['volumentotal'] = volumenCalidad + volumenReproceso
            form_data['categoria_trz'] = 'A'
            cache.delete('form_delete')
            return render(request,'previsualFNG.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = fingerForm(form_data) if form_data else fingerForm()
    return render(request,'fingerForm.html',{'form': form, 'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})              

def fingerInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = fingerForm(request.POST or None)
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
        nuevo_form = fingerForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_calidad = request.POST.get('piezascalidad')
        piezas_reproceso = request.POST.get('piezasreproceso')
        suma_salida = float(piezas_calidad) + float(piezas_reproceso)
        if piezas_entrada == '' or piezas_calidad == '' or piezas_reproceso == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_entrada) < 0 or float(piezas_calidad) < 0 or float(piezas_reproceso) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if suma_salida > float(piezas_entrada):
            messages.error(request, 'Piezas calidad mas reproceso no puede ser superior a entrada')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
            cantidad_trz_disp = madera_anterior.piezas_trza
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 6
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                if(instance.piezasentrada != None):
                    instance.volumenentrada = calcularVolumen(instance.codigo_madera_ant,instance.piezasentrada)
                if(instance.piezascalidad != None):
                    instance.volumencalidad = calcularVolumen(instance.codigo_madera,instance.piezascalidad)
                if(instance.piezasreproceso != None):
                    instance.volumenreproceso =  calcularVolumen(instance.codigo_madera,instance.piezasreproceso)

                instance.volumentotal = instance.volumencalidad + instance.volumenreproceso


            instance.id_area = 1
            instance.id_centrotrabajo = 6
            instance.categoria_trz = 'A'
            for i in Maquina.objects.raw(
                """
                SELECT "id_maquina","nombreMaquina" FROM "Maquina"
                WHERE "centroTrabajoMaquina" = 'Finger'
                """
            ):
                if (i.nombremaquina == instance.nombre_maquina):
                    instance.nombre_centrotrabajo = i.centrotrabajomaquina
                    instance.id_maquina = i.id_maquina

            if madera_anterior.id_centrotrabajo == 5:
                if instance.piezasentrada > cantidad_trz_disp:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
            
            if instance.piezasentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
            instance.save()
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezascalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas_trz-a" = "piezas_trz-a" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
        
            connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" + %s WHERE "codigo_madera" = %s
                """,(instance.piezasreproceso, instance.codigo_madera)) 

            actualizarMadera() 
            cache.delete('form_data')
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
   
        return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = fingerForm(form_data)
        return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

class MoldureraFormView(FormView):
    template_name = 'moldureraForm.html'
    form_class = moldureraForm
    success_url = '/Rema/Moldurera'

    def form_valid(self, form):
        form_data = form.cleaned_data
        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionMOL')
        return super().form_valid(form)

def previsualizacionMOL(request):
    info_maquinas = Maquina.objects.all()
    info_maderas = Maderas.objects.all()

    if request.method == 'POST':
        form = moldureraForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenentrada': '0',
                            'volumencalidad': '0',
                            'volumenrechazoproc':'0',
                            'volumentotal':'0'})
        nuevo_formVis = moldureraForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_calidad = request.POST.get('piezascalidad')
        piezas_rechazo = request.POST.get('piezasrechazoproc')
        suma_salida = float(piezas_calidad) + float(piezas_rechazo)

        if piezas_entrada == '' or piezas_calidad == '' or piezas_rechazo == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if float(piezas_entrada) < 0 or float(piezas_calidad) < 0 or float(piezas_rechazo) < 0:
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if suma_salida > float(piezas_entrada):
            messages.error(request, 'Piezas calidad más rechazo no puede ser superior a entrada')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_calidad = float(request.POST.get('piezascalidad'))
            piezas_rechazo = float(request.POST.get('piezasrechazoproc'))
            codigo_madera = request.POST.get('codigo_madera')
            codigo_madera_ant = request.POST.get('codigo_madera_ant')
            id_madera = None
            id_maquina = None

            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 8"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Moldurera'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i.id_maquina
                    break

            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 5
            volumenEntrada = calcularVolumen(codigo_madera_ant, piezas_entrada)
            volumenCalidad = calcularVolumen(codigo_madera, piezas_calidad)
            volumenRechazo = calcularVolumen(codigo_madera, piezas_rechazo)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumencalidad'] = volumenCalidad
            form_data['volumenrechazoproc'] = volumenRechazo
            form_data['volumentotal'] = volumenCalidad + volumenRechazo

            cache.delete('form_data')
            return render(request, 'previsualMOL.html', {'form_data': form_data, 'form': nuevo_formVis})

    else:
        form_data = cache.get('form_data')
        form = moldureraForm(form_data) if form_data else moldureraForm()

    return render(request, 'moldureraForm.html', {'form': form, 'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
def moldureraInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        
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
        nuevo_form = moldureraForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_calidad = request.POST.get('piezascalidad')
        piezas_rechazo = request.POST.get('piezasrechazoproc')
        suma_salida = float(piezas_calidad) + float(piezas_rechazo)
        if piezas_entrada == '' or piezas_calidad == '' or piezas_rechazo == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_entrada) < 0 or float(piezas_calidad) < 0 or float(piezas_rechazo) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if suma_salida > float(piezas_entrada):
            messages.error(request,'Piezas calidad más rechazo no puede ser superior a entrada')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
       
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 8
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

                if (instance.piezasentrada != None):    
                    instance.volumenentrada = calcularVolumen(instance.codigo_madera_ant,instance.piezasentrada)
                    
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
            
            if instance.piezasentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})

            instance.save()
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezascalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            

            actualizarMadera()
            cache.delete('form_data')   
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})
 
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = moldureraForm(form_data)
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'form': form_data})

class ReprocesoFormView(FormView):
    template_name = 'reprocesoForm.html'
    form_class = reprocesoForm
    success_url = '/Rema/Reproceso'

    def form_valid(self, form):
        form_data = form.cleaned_data
        if 'ingresar' in self.request.POST:
            form.save()
        if 'previsualizar' in self.request.POST:
            return redirect('previsualizacionRPR')   
        return super().form_valid(form)

def previsualizacionRPR(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    if request.method == 'POST':
        form = reprocesoForm(request.POST)
        update_data = request.POST.copy()
        p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida': '0',
                            'volumentotal':'0'})
        nuevo_formVis = reprocesoForm(update_data)
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_salida) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')
            id_madera = None
            id_maquina = None
            categoria_trz = request.POST.get('categoria_trz')
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 7"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            for i in Maquina.objects.raw("""SELECT "id_maquina", "nombreMaquina" FROM "Maquina" WHERE "centroTrabajoMaquina" = 'Reproceso'"""):
                if i.nombremaquina == request.POST.get('nombre_maquina'):
                    id_maquina = i.id_maquina
                    break

            form_data['id_madera'] = id_madera
            form_data['id_maquina'] = id_maquina    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 7    
            volumenSalida = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumensalida'] = volumenSalida
            form_data['volumentotal'] = volumenSalida
            form_data['categoria_trz'] = categoria_trz
            cache.delete('form_data')
            return render(request,'previsualRPR.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = reprocesoForm(form_data) if form_data else reprocesoForm()
    return render(request,'reprocesoForm.html',{'form':form,'inf_maquinas': info_maquinas,'inf_maderas':info_maderas})        



def reprocesoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida':'0',
                            'volumentotal':'0'})
        nuevo_form = reprocesoForm(update_data)
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_salida) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.reproceso
            cantidad_disponibleTRZB = madera_anterior.piezas_trzb
            cantidad_disponibleTRZC = madera_anterior.piezas_trzc
            categoria_trz = request.POST.get('categoria_trz')
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
            instance.categoria_trz = categoria_trz
            
            if instance.categoria_trz == 'B':
                instance.piezas_trz_b = instance.piezassalida
                if instance.piezassalida > cantidad_disponibleTRZB:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas_trz-b" = "piezas_trz-b" - %s WHERE "codigo_madera" = %s 
                """,(instance.piezas_trz_b, instance.codigo_madera_ant))
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))
            elif instance.categoria_trz == 'C': 
                instance.piezas_trz_c = instance.piezassalida
                if instance.piezassalida > cantidad_disponibleTRZC:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas_trz-c" = "piezas_trz-c" - %s WHERE "codigo_madera" = %s 
                """,(instance.piezassalida, instance.codigo_madera_ant))
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))
            
            elif instance.categoria_trz == 'A':
                if instance.piezassalida > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
                connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" - %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera_ant))
                
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))
                    
                
                
            instance.save()
            actualizarMadera()
            cache.delete('form_data')
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form}) 
        return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
    else:
        form_data = cache.get('form_data')
        if form_data:
            nuevo_form = reprocesoForm(form_data)
        return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'form':form_data})

    