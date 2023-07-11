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
            messages.error(request,'Asegurese de llenar todos los campos')
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
                            'volumenease':'0',
                            'volumentotal':'0'})
        nuevo_formVis = entradaAserraderoForm(update_data)
        piezas_ease = request.POST.get('piezasease')
        if piezas_ease == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(piezas_ease) < 0: 
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_ease = float(request.POST.get('piezasease'))
            codigo_madera = request.POST.get('codigo_madera')

            id_madera = None
            for i in Maderas.objects.raw("""SELECT "id_madera", "codigo_madera" FROM "Maderas" WHERE "id_centroTrabajo" = 1"""):
                if i.codigo_madera == codigo_madera:
                    id_madera = i.id_madera
                    break

            form_data['id_madera'] = id_madera    
            form_data['id_area'] = 1
            form_data['id_centrotrabajo'] = 1

            volumen_salidaEASE = calcularVolumenEASE(codigo_madera,piezas_ease)
            form_data['volumenease'] = volumen_salidaEASE
            form_data['volumentotal'] = volumen_salidaEASE

            cache.delete('form_data')
            return render(request, 'previsualEASE.html',{'form_data': form_data, 'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = entradaAserraderoForm(form_data) if form_data else entradaAserraderoForm()
    return render(request,'entradaAseForm.html',{'form':form,'maquinas':info_maquinas,'maderas':info_maderas})    
    

def entradaAserraderoInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('diametro').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'idproceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumenease':'0',
                            'volumentotal':'0'})
        nuevo_form = entradaAserraderoForm(update_data)
        piezas_ease = request.POST.get('piezasease')
        if piezas_ease == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(piezas_ease) < 0: 
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
                    instance.volumenease = calcularVolumenEASE(instance.codigo_madera,instance.piezasease)
                instance.volumentotal = instance.volumenease

                instance.id_area = 1
                instance.id_centrotrabajo = 1
                instance.nombre_centrotrabajo = 'EntradaAserradero'
            instance.save()
            
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezasease, instance.codigo_madera))
            
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenxPieza" = ("diametro" * "diametro" * "largo") /10000 WHERE "codigo_madera" LIKE 'EASE%'
            """)
            connection.cursor().execute("""
            UPDATE "Maderas"
            SET "volumenTotal" = "volumenxPieza"*"piezas"
            """)

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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
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
                            'volumentotal':'0'})
        nuevo_formVis = aserraderoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_salida = request.POST.get('volumensalida')
        if volumen_salida == '' or volumen_entrada == '':
            messages.error(request, 'No se puede previsualizar sin piezas ingresadas')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(volumen_salida) < 0 or float(volumen_entrada) < 0:
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        
        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese la Fecha correctamente')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})


        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_entrada = float(request.POST.get('volumenentrada'))
            volumen_salida = float(request.POST.get('volumensalida'))
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
            #volumenEntrada = calcularVolumenEASE(codigo_madera_ant,piezas_entrada)    
            #volumen = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumensalida'] = float(volumen_salida)
            form_data['volumenentrada'] = float(volumen_entrada)
            form_data['volumentotal'] = float(volumen_salida)
            

            cache.delete('form_data')
            return render(request, 'previsualizacion.html', {'form_data': form_data, 'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = aserraderoForm()
    
    return render(request,'salidaAseForm.html',{'form':form,'maquinas':info_maquinas,'maderas':info_maderas}) 


def aserraderoInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumentotal':'0'})
        nuevo_form = aserraderoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_salida = request.POST.get('volumensalida')
        if volumen_salida == '' or volumen_entrada == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todas las piezas')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(volumen_salida) < 0 or float(volumen_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese la Fecha correctamente')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant).order_by('codigo_madera').values()
            cantidad_disponible = madera_anterior.piezas
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 2
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

            
            instance.volumentotal = instance.volumensalida

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
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
            """,(instance.volumensalida, instance.codigo_madera))
            
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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
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
                            'volumentotal':'0'})
        nuevo_formVis = secadoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_salida = request.POST.get('volumensalida')

        if volumen_entrada == '' or volumen_salida == '':
            messages.error(request, 'No se puede previsualizar sin piezas ingresadas')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(volumen_salida) < 0 or float(volumen_entrada) < 0 :
            messages.error(request, 'Cantidad inválida en voluemn (menor a cero)')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(volumen_salida) > float(volumen_entrada):
            messages.error(request, 'Volumen de salida no puede ser mayor a la entrada')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_entrada = float(request.POST.get('volumenentrada'))
            volumen_salida = float(request.POST.get('volumensalida'))
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
            form_data['volumenentrada'] = float(volumen_entrada)
            form_data['volumensalida'] = float(volumen_salida)
            cache.delete('form_data')

            return render(request,'previsualSec.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = secadoForm(form_data) if form_data else secadoForm()
    return render(request,'secadoForm.html',{'form':form,'maquinas':info_maquinas,'maderas':info_maderas})    

def secadoInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumentotal':'0',})
        nuevo_form = secadoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_salida = request.POST.get('volumensalida')

        if volumen_entrada == '' or volumen_salida == '':
            messages.error(request, 'No se puede Ingresar sin agregar todos los volumenes')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(volumen_salida) < 0 or float(volumen_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de volumen (menor a cero)')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(volumen_salida) > float(volumen_entrada):
            messages.error(request,'Volumen salida no puede ser mayor a la entrada')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
 
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant).order_by('codigo_madera').values()
            cantidad_disponible = madera_anterior.volumentotal
            cantidad_disponibleCEP = madera_anterior.reproceso
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 3
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                


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


            if instance.volumenentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de volumen ingresado es superior a la disponible')
                return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})
            if instance.codigo_madera_ant[0] == 'C':
                if instance.volumenentrada > cantidad_disponibleCEP:
                    messages.error(request, 'La cantidad en volumen de CEP ingresado es superior a la disponible')
                    return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas,'nuevo_form':nuevo_form})    
            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
            """,(instance.volumensalida, instance.codigo_madera))
            if instance.codigo_madera_ant[0] != 'C':
                connection.cursor().execute("""
                UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" - %s WHERE "codigo_madera" = %s
                """,(instance.volumenentrada,instance.codigo_madera_ant))
            
            if instance.codigo_madera_ant[0] == 'C':
                connection.cursor().execute("""
                    UPDATE "Maderas"
                    SET "reproceso" = "reproceso" - %s
                    WHERE "codigo_madera" = %s
                    """,(instance.volumenentrada, instance.codigo_madera_ant))
                
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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
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
                            'volumentotal':'0',})
        nuevo_formVis = cepilladoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_salida = request.POST.get('volumensalida')
        volumen_rechazohum = request.POST.get('volumenrechazohum')
        volumen_rechazodef = request.POST.get('volumenrechazodef')
        volumen_rechazoproc = request.POST.get('volumenrechazoproc')
        suma_salida = float(volumen_salida) + float(volumen_rechazodef) + float(volumen_rechazohum) + float(volumen_rechazoproc)
        if volumen_entrada == '' or volumen_salida == '' or volumen_rechazodef == '' or volumen_rechazohum == '' or volumen_rechazoproc == '':
                messages.error(request, 'No se puede previsualizar si no se agregan todos los volumenes')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(volumen_salida) < 0 or float(volumen_entrada) < 0 or float(volumen_rechazodef) < 0 or float(volumen_rechazohum) < 0 or float(volumen_rechazoproc) < 0 :
            messages.error(request, 'Cantidad inválida de volumen (menor a cero)')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if suma_salida > float(volumen_entrada):
            messages.error(request,'Volumen salida más rechazos no pueden ser mayor a la entrada')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_entrada = float(request.POST.get('volumenentrada'))
            volumen_salida = float(request.POST.get('volumensalida'))
            volumen_rechazohum = float(request.POST.get('volumenrechazohum'))
            volumen_rechazodef = float(request.POST.get('volumenrechazodef'))
            volumen_rechazoproc = float(request.POST.get('volumenrechazoproc'))

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

            
            form_data['volumenentrada'] = float(volumen_entrada)
            form_data['volumensalida'] = float(volumen_salida)
            form_data['volumenrechazohum'] = float(volumen_rechazohum)
            form_data['volumenrechazodef'] = float(volumen_rechazodef)
            form_data['volumenrechazoproc'] = float(volumen_rechazoproc)

            cache.delete('form_data')
            return render(request,'previsualCep.html',{'form_data': form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = cepilladoForm(form_data) if form_data else cepilladoForm()
    return render(request,'cepilladoForm.html',{'form':form,'inf_maquinas':info_maquinas,'inf_maderas':info_maderas})

def cepilladoInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()

        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumentotal':'0',
                            })
        nuevo_form = cepilladoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_salida = request.POST.get('volumensalida')
        volumen_rechazohum = request.POST.get('volumenrechazohum')
        volumen_rechazodef = request.POST.get('volumenrechazodef')
        volumen_rechazoproc = request.POST.get('volumenrechazoproc')
        suma_salida = float(volumen_salida) + float(volumen_rechazodef) + float(volumen_rechazohum) + float(volumen_rechazoproc)
        if volumen_entrada == '' or volumen_salida == '' or volumen_rechazodef == '' or volumen_rechazohum == '' or volumen_rechazoproc == '':
                messages.error(request, 'No se puede Ingresar si no se agregan todos los volumenes')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if suma_salida > float(volumen_entrada):
            messages.error(request, 'Suma de volumenes salida más rechazos no puede ser superior a entrada')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if float(volumen_salida) < 0 or float(volumen_entrada) < 0 or float(volumen_rechazodef) < 0 or float(volumen_rechazohum) < 0 or float(volumen_rechazoproc) < 0 :
            messages.error(request, 'Cantidad inválida de volumenes (menor a cero)')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
           

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant).order_by('codigo_madera').values()
            cantidad_disponible = madera_anterior.volumentotal
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 4
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                

                
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
            
            if instance.volumenentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de volumen ingresado es superior a la disponible')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" + %s WHERE "codigo_madera" = %s
                """,(instance.piezasrechazohum, instance.codigo_madera)) 

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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
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
                            'volumentotal':'0',
                            })
        nuevo_formVis = trozadoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_cat_a = request.POST.get('volumen_trz_a')
        volumen_cat_b = request.POST.get('volumen_trz_b')
        volumen_cat_c = request.POST.get('volumen_trz_c')
        volumen_cat_d = request.POST.get('volumen_trz_d')
        sumaCategorias = float(volumen_cat_a)+float(volumen_cat_b)+float(volumen_cat_c)+float(volumen_cat_d)
        if volumen_entrada == '' or volumen_cat_a == '' or volumen_cat_b=='' or volumen_cat_c == '' or volumen_cat_d=='':
            messages.error(request, 'No se puede previsualizar si no se agregan todos los volumenes')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(volumen_cat_a) < 0 or float(volumen_cat_b) < 0 or float(volumen_cat_c) < 0 or float(volumen_cat_d) < 0 or float(volumen_entrada) < 0 :
            messages.error(request, 'Cantidad inválida en volumen (menor a cero)')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if sumaCategorias > float(volumen_entrada):
            messages.error(request, 'Suma de las categorias no puede ser superior a entrada')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
            
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_entrada = float(request.POST.get('volumenentrada'))
            volumen_cat_a = request.POST.get('volumen_trz_a')
            volumen_cat_b = request.POST.get('volumen_trz_b')
            volumen_cat_c = request.POST.get('volumen_trz_c')
            volumen_cat_d = request.POST.get('volumen_trz_d')
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
            form_data['volumenentrada'] = float(volumen_entrada)
            
            form_data['volumen_trz_a'] = float(volumen_cat_a)
            form_data['volumen_trz_b'] = float(volumen_cat_b)
            form_data['volumen_trz_c'] = float(volumen_cat_c)
            form_data['volumen_trz_d'] = float(volumen_cat_d)
            form_data['volumensalida'] = form_data['volumen_trz_a'] +form_data['volumen_trz_b'] +form_data['volumen_trz_c'] +form_data['volumen_trz_d']
            form_data['volumentotal'] = float(form_data['volumensalida'])
            


            print(form_data)
            cache.delete('form_data')
            return render(request,'previsualTRZ.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = trozadoForm(form_data) if form_data else trozadoForm()
    return render(request,'trozadoForm.html',{'form':form,'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})



def trozadoInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('espesor').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumentotal':'0',
                            })
        nuevo_form = trozadoForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_cat_a = request.POST.get('volumen_trz_a')
        volumen_cat_b = request.POST.get('volumen_trz_b')
        volumen_cat_c = request.POST.get('volumen_trz_c')
        volumen_cat_d = request.POST.get('volumen_trz_d')
        sumaCategorias = float(volumen_cat_a)+float(volumen_cat_b)+float(volumen_cat_c)+float(volumen_cat_d)

        if volumen_entrada == '' or volumen_cat_a == '' or volumen_cat_b == '' or volumen_cat_c == '' or volumen_cat_d == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todos los volumenes')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})
        if float(volumen_cat_a) < 0 or float(volumen_cat_b) < 0 or float(volumen_cat_c) < 0 or float(volumen_cat_d) < 0 or float(volumen_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de volumenes (menor a cero)')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})
        if sumaCategorias > float(volumen_entrada):
            messages.error(request, 'Suma de las categorias no puede ser superior a entrada')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})

        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
          
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1
            instance.codigo_madera_ant = update_data['codigo_madera_ant']

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant).order_by('codigo_madera').values()
            cantidad_disponible = madera_anterior.volumentotal
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 5
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

            instance.volumensalida = instance.volumen_trz_a + instance.volumen_trz_b + instance.volumen_trz_c + instance.volumen_trz_d

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
            
            if instance.volumenentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de volumen ingresado es superior al disponible')
                return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})



            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
            """,(instance.volumensalida, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumen_trz-a" = "volumen_trz-a" + %s WHERE "codigo_madera" = %s
            """,(instance.volumen_trz_a, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumen_trz-b" = "volumen_trz-b" + %s WHERE "codigo_madera" = %s
            """,(instance.volumen_trz_b, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumen_trz-c" = "volumen_trz-c" + %s WHERE "codigo_madera" = %s
            """,(instance.volumen_trz_c, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumen_trz-d" = "volumen_trz-d" + %s WHERE "codigo_madera" = %s
            """,(instance.volumen_trz_d, instance.codigo_madera))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumentotal" = "volumenTotal" - %s WHERE "codigo_madera" = %s
            """,(instance.volumenentrada,instance.codigo_madera_ant))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = "reproceso" + %s + %s WHERE "codigo_madera" = %s
            """,(instance.volumen_trz_b,instance.volumen_trz_c,instance.codigo_madera))

             
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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('codigo_madera').values()
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
                            'volumentotal':'0'})
        nuevo_formVis = fingerForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_calidad = request.POST.get('volumencalidad')
        volumen_reproceso = request.POST.get('volumenreproceso')
        suma_salida = float(volumen_calidad) + float(volumen_reproceso)
        if volumen_entrada == '' or volumen_calidad == '' or volumen_reproceso == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todos los volumenes')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(volumen_entrada) < 0 or float(volumen_calidad) < 0 or float(volumen_reproceso) < 0 :
            messages.error(request, 'Cantidad inválida de volumenes (menor a cero)')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if suma_salida > float(volumen_entrada):
            messages.error(request,'Piezas calidad más reproceso no puede ser superior a entrada')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_entrada = float(request.POST.get('volumenentrada'))
            volumen_calidad = float(request.POST.get('volumencalidad'))
            volumen_reproceso = float(request.POST.get('volumenreproceso'))
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
            form_data['volumenentrada'] = float(volumen_entrada)
            form_data['volumencalidad'] = float(volumen_calidad)
            form_data['volumenreproceso'] = float(volumen_reproceso)
            form_data['volumentotal'] = float(volumen_calidad) + float(volumen_reproceso)
            form_data['categoria_trz'] = 'A'
            cache.delete('form_delete')
            return render(request,'previsualFNG.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = fingerForm(form_data) if form_data else fingerForm()
    return render(request,'fingerForm.html',{'form': form, 'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})              

def fingerInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('codigo_madera').values()
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
                            'volumentotal':'0'
                            })
        nuevo_form = fingerForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_calidad = request.POST.get('volumencalidad')
        volumen_reproceso = request.POST.get('volumenreproceso')
        suma_salida = float(volumen_calidad) + float(volumen_reproceso)
        if volumen_entrada == '' or volumen_calidad == '' or volumen_reproceso == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todos los volumenes')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(volumen_entrada) < 0 or float(volumen_calidad) < 0 or float(volumen_reproceso) < 0 :
            messages.error(request, 'Cantidad inválida de volumenes (menor a cero)')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if suma_salida > float(volumen_entrada):
            messages.error(request, 'Volumen calidad mas reproceso no puede ser superior a entrada')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant).order_by('codigo_madera').values()
            cantidad_disponible = madera_anterior.volumentotal
            cantidad_trz_disp = madera_anterior.volumen_trza
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 6
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
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
                if instance.volumenentrada > cantidad_trz_disp:
                    messages.error(request, 'La cantidad de volumen ingresado es superior a la disponible')
                    return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
            
            if instance.volumenentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de volumen ingresado es superior a la disponible')
                    return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
            instance.save()
            connection.cursor().execute("""
                UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
                """,(instance.volumencalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumen_trz-a" = "volumen_trz-a" - %s WHERE "codigo_madera" = %s
            """,(instance.volumenentrada,instance.codigo_madera_ant))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" - %s WHERE "codigo_madera" = %s
            """,(instance.volumenentrada,instance.codigo_madera_ant))
        
            connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" + %s WHERE "codigo_madera" = %s
                """,(instance.piezasreproceso, instance.codigo_madera)) 

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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('codigo_madera').values()

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
                            'volumentotal':'0'})
        nuevo_formVis = moldureraForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_calidad = request.POST.get('volumencalidad')
        volumen_rechazo = request.POST.get('volumenrechazoproc')
        suma_salida = float(volumen_calidad) + float(volumen_rechazo)

        if volumen_entrada == '' or volumen_calidad == '' or volumen_rechazo == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todos los volumenes')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if float(volumen_entrada) < 0 or float(volumen_calidad) < 0 or float(volumen_rechazo) < 0:
            messages.error(request, 'Cantidad inválida de volumen (menor a cero)')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if suma_salida > float(volumen_entrada):
            messages.error(request, 'Volumen calidad más rechazo no puede ser superior a entrada')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request, 'moldureraForm.html', {'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_entrada = float(request.POST.get('volumenentrada'))
            volumen_calidad = float(request.POST.get('volumencalidad'))
            volumen_rechazo = float(request.POST.get('volumenrechazoproc'))
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
            form_data['volumenentrada'] = float(volumen_entrada)
            form_data['volumencalidad'] = float(volumen_calidad)
            form_data['volumenrechazoproc'] = float(volumen_rechazo)
            form_data['volumentotal'] = float(volumen_calidad) + float(volumen_rechazo)

            cache.delete('form_data')
            return render(request, 'previsualMOL.html', {'form_data': form_data, 'form': nuevo_formVis})

    else:
        form_data = cache.get('form_data')
        form = moldureraForm(form_data) if form_data else moldureraForm()

    return render(request, 'moldureraForm.html', {'form': form, 'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
def moldureraInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('codigo_madera').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumentotal':'0',
                            })
        nuevo_form = moldureraForm(update_data)
        volumen_entrada = request.POST.get('volumenentrada')
        volumen_calidad = request.POST.get('volumencalidad')
        volumen_rechazo = request.POST.get('volumenrechazoproc')
        suma_salida = float(volumen_calidad) + float(volumen_rechazo)
        if volumen_entrada == '' or volumen_calidad == '' or volumen_rechazo == '':
            messages.error(request, 'No se puede Ingresar si no se agregan todos los volumenes')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(volumen_entrada) < 0 or float(volumen_calidad) < 0 or float(volumen_rechazo) < 0 :
            messages.error(request, 'Cantidad inválida de volumenes (menor a cero)')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if suma_salida > float(volumen_entrada):
            messages.error(request,'Volumen calidad más rechazo no puede ser superior a entrada')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
       
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant).order_by('codigo_madera').values()
            cantidad_disponible = madera_anterior.volumentotal
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 8
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera

                
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
            
            if instance.volumenentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de volumen ingresado es superior al disponible')
                    return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas, 'nuevo_form':nuevo_form})

            instance.save()
            connection.cursor().execute("""
                UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
                """,(instance.volumencalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" - %s WHERE "codigo_madera" = %s
            """,(instance.volumenentrada,instance.codigo_madera_ant))
            

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
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('codigo_madera').values()
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
                            'volumentotal':'0'})
        nuevo_formVis = reprocesoForm(update_data)
        volumen_salida = request.POST.get('volumensalida')
        if volumen_salida == '':
            messages.error(request, 'No se puede previsualizar si no se agrega el volumen')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(volumen_salida) < 0 :
            messages.error(request, 'Cantidad inválida de volumen (menor a cero)')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            volumen_salida = float(request.POST.get('volumensalida'))
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
            form_data['volumensalida'] = float(volumen_salida)
            form_data['volumentotal'] = float(volumen_salida)
            form_data['categoria_trz'] = categoria_trz
            cache.delete('form_data')
            return render(request,'previsualRPR.html',{'form_data':form_data,'form':nuevo_formVis})
    else:
        form_data = cache.get('form_data')
        form = reprocesoForm(form_data) if form_data else reprocesoForm()
    return render(request,'reprocesoForm.html',{'form':form,'inf_maquinas': info_maquinas,'inf_maderas':info_maderas})        



def reprocesoInfo(request):
    info_maquinas = Maquina.objects.all().order_by('nombremaquina').values()
    info_maderas = Maderas.objects.all().order_by('codigo_madera').values()
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumentotal':'0'})
        nuevo_form = reprocesoForm(update_data)
        volumen_salida = request.POST.get('volumensalida')
        if volumen_salida == '':
            messages.error(request, 'No se puede Ingresar si no se agrega el volumen')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if float(volumen_salida) < 0 :
            messages.error(request, 'Cantidad inválida de volumen (menor a cero)')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
        
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.reproceso
            cantidad_disponibleTRZB = madera_anterior.volumen_trzb
            cantidad_disponibleTRZC = madera_anterior.volumen_trzc
            categoria_trz = request.POST.get('categoria_trz')
            for i in Maderas.objects.raw(
                """
                SELECT "id_madera", "codigo_madera", "espesor","ancho","largo" FROM "Maderas"
                WHERE "id_centroTrabajo" = 8
                """
            ):
                if (i.codigo_madera == instance.codigo_madera):
                    instance.id_madera = i.id_madera
                
        
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
                instance.volumen_trz_b = instance.volumensalida
                if instance.volumensalida > cantidad_disponibleTRZB:
                    messages.error(request, 'La cantidad de volumen ingresado es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
                connection.cursor().execute("""
                UPDATE "Maderas" SET "volumen_trz-b" = "volumen_trz-b" - %s WHERE "codigo_madera" = %s 
                """,(instance.volumen_trz_b, instance.codigo_madera_ant))
                connection.cursor().execute("""
                UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
                """,(instance.volumensalida, instance.codigo_madera))
            elif instance.categoria_trz == 'C': 
                instance.volumen_trz_c = instance.volumensalida
                if instance.volumensalida > cantidad_disponibleTRZC:
                    messages.error(request, 'La cantidad de volumen ingresado es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
                connection.cursor().execute("""
                UPDATE "Maderas" SET "volumen_trz-c" = "volumen_trz-c" - %s WHERE "codigo_madera" = %s 
                """,(instance.volumensalida, instance.codigo_madera_ant))
                connection.cursor().execute("""
                UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
                """,(instance.volumensalida, instance.codigo_madera))
            
            elif instance.categoria_trz == 'A':
                if instance.volumensalida > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas,'nuevo_form':nuevo_form})
                connection.cursor().execute("""
                UPDATE "Maderas" SET "reproceso" = "reproceso" - %s WHERE "codigo_madera" = %s
                """,(instance.volumensalida, instance.codigo_madera_ant))
                
                connection.cursor().execute("""
                UPDATE "Maderas" SET "volumenTotal" = "volumenTotal" + %s WHERE "codigo_madera" = %s
                """,(instance.volumensalida, instance.codigo_madera))
                    
                
                
            instance.save()
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

    