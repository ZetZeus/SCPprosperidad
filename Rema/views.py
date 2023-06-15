from django.shortcuts import render, redirect
from django.db.models import Max
from django.contrib import messages
from django.http import HttpResponse
from django.db import connection
from formtools.preview import FormPreview
from formtools.wizard.views import SessionWizardView
from django.views.generic.edit import FormView



# Create your views here.
from .models import Centrotrabajo,Area, Maquina, Maderas, Proceso
from .forms import entradaAserraderoForm,aserraderoForm,secadoForm,cepilladoForm,trozadoForm,fingerForm,moldureraForm,reprocesoForm, nuevaMadera



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
     
            connection.cursor().execute("""
            UPDATE "Maderas" SET "reproceso" = 0 WHERE "codigo_madera" = %s
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
    volumen = (madera.espesor * madera.ancho * madera.largo * piezas_recibidas) / 1000000    
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
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = entradaAserraderoForm(request.POST or None)
        update_data = request.POST.copy()
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

            return render(request, 'previsualEASE.html',{'form_data': form_data})
    else:
        form = entradaAserraderoForm()
    return redirect('entradaAserraderoInfo')    
    

def entradaAserraderoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = entradaAserraderoForm(request.POST or None)
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
            instance.save()
            
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))
            
            actualizarMadera()
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
    else:

        return render(request,'entradaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

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
                            'volumentotal':'0'})
        nuevo_formVis = aserraderoForm(update_data)
        piezas_salida = request.POST.get('piezassalida')
        if piezas_salida == '':
            messages.error(request, 'No se puede previsualizar sin piezas ingresadas')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        if float(piezas_salida) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if request.POST.get('fecha') == '':
            messages.error(request, 'Ingrese la Fecha correctamente')
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})


        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')
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
            volumen = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumensalida'] = volumen
            form_data['volumentotal'] = volumen


            return render(request, 'previsualizacion.html', {'form_data': form_data})
    else:
        form = aserraderoForm()
    
    return redirect('aserraderoInfo') 



def aserraderoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = aserraderoForm(request.POST or None)
        update_data = request.POST.copy()
        idProceso = p+1
        update_data.update({'id_proceso': idProceso,
                            'id_madera':'0',
                            'id_centrotrabajo':'0',
                            'id_area':'0',
                            'id_maquina': '0',
                            'volumensalida': '0',
                            'volumentotal':'0'})
        nuevo_form = aserraderoForm(update_data)
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
            volumen = calcularVolumen(instance.codigo_madera,instance.piezassalida)
            instance.volumensalida = volumen
            instance.volumentotal = volumen

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

            if instance.piezassalida > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})            
            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera_ant))
            actualizarMadera()
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
    
    else:
        return render(request,'salidaAseForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})


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
        
        
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
        
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')
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
            volumenEntrada = calcularVolumen(codigo_madera,piezas_entrada)
            volumenSalida = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumensalida'] = volumenSalida
            form_data['piezasentrada'] = piezas_entrada

            return render(request,'previsualSec.html',{'form_data':form_data})
    else:
        form = secadoForm()
    return redirect('secadoInfo')    

def secadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = secadoForm(request.POST or None)
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

        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
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

                if instance.piezasentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
                instance.save()
                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezassalida, instance.codigo_madera))

                connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
                """,(instance.piezasentrada,instance.codigo_madera_ant))
              
                actualizarMadera()

                
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
   
        return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})
    


    else:
        return render(request,'secadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})


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
        if piezas_entrada == '' or piezas_salida == '' or piezas_rechazodef == '' or piezas_rechazohum == '' or piezas_rechazoproc == '':
                messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 or float(piezas_rechazodef) < 0 or float(piezas_rechazohum) < 0 or float(piezas_rechazoproc) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
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

            
            volumenEntrada = calcularVolumen(codigo_madera,piezas_entrada)
            volumenSalida = calcularVolumen(codigo_madera,piezas_salida)
            volumenRechazoHum = calcularVolumen(codigo_madera,piezas_rechazohum)
            volumenRechazoDef = calcularVolumen(codigo_madera,piezas_rechazodef)
            volumenRechazoProc = calcularVolumen(codigo_madera,piezas_rechazoproc)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumensalida'] = volumenSalida
            form_data['volumenrechazohum'] = volumenRechazoHum
            form_data['volumenrechazodef'] = volumenRechazoDef
            form_data['volumenrechazoproc'] = volumenRechazoProc

            return render(request,'previsualCep.html',{'form_data': form_data})
    else:
        form = cepilladoForm()
    return redirect('cepilladoInfo')



def cepilladoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = cepilladoForm(request.POST or None)
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
            
            if instance.piezasentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            

            actualizarMadera() 
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
               
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

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
                            'volumentotal':'0'})
        nuevo_formVis = trozadoForm(update_data)
        piezas_entrada = request.POST.get('piezasentrada')
        piezas_salida = request.POST.get('piezassalida')
        if piezas_entrada == '' or piezas_salida == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_salida) < 0 or float(piezas_entrada) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
            
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_salida = float(request.POST.get('piezassalida'))
            codigo_madera = request.POST.get('codigo_madera')
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
            volumenEntrada = calcularVolumen(codigo_madera,piezas_entrada)
            volumenSalida = calcularVolumen(codigo_madera,piezas_salida)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumensalida'] = volumenSalida
            form_data['volumentotal'] = volumenSalida

            return render(request,'previsualTRZ.html',{'form_data':form_data})
    else:
        form = trozadoForm()
    return redirect('trozadoInfo')



def trozadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = trozadoForm(request.POST or None)
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
        nuevo_form = trozadoForm(update_data)
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
            
            if instance.piezasentrada > cantidad_disponible:
                messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

            instance.save()

            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))

            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            
            

            actualizarMadera() 
        else:
            messages.success(request, ('Error al ingresar'))
            return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'trozadoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})


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
        if piezas_entrada == '' or piezas_calidad == '' or piezas_reproceso == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_entrada) < 0 or float(piezas_calidad) < 0 or float(piezas_reproceso) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
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
            volumenEntrada = calcularVolumen(codigo_madera,piezas_entrada)
            volumenCalidad = calcularVolumen(codigo_madera,piezas_calidad)
            volumenReproceso = calcularVolumen(codigo_madera, piezas_reproceso)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumencalidad'] = volumenCalidad
            form_data['volumenreproceso'] = volumenReproceso
            form_data['piezasentrada'] = piezas_entrada
            form_data['volumentotal'] = volumenCalidad + volumenReproceso

            return render(request,'previsualFNG.html',{'form_data':form_data})
    else:
        form = fingerForm()
    return redirect('fingerInfo')              

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
        if nuevo_form.is_valid():
            instance = nuevo_form.save(commit=False)
            instance.id_proceso = p+1

            madera_anterior = Maderas.objects.get(codigo_madera = instance.codigo_madera_ant)
            cantidad_disponible = madera_anterior.piezas
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

            if instance.piezasentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'fingerForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
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
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
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
        if piezas_entrada == '' or piezas_calidad == '' or piezas_rechazo == '':
            messages.error(request, 'No se puede previsualizar si no se agregan todas las piezas')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if float(piezas_entrada) < 0 or float(piezas_calidad) < 0 or float(piezas_rechazo) < 0 :
            messages.error(request, 'Cantidad inválida de piezas (menor a cero)')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if request.POST.get('fecha') == '':    
            messages.error(request, 'Ingrese fecha correctamente')
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
        if nuevo_formVis.is_valid():
            form_data = nuevo_formVis.cleaned_data
            piezas_entrada = float(request.POST.get('piezasentrada'))
            piezas_calidad = float(request.POST.get('piezascalidad'))
            piezas_rechazo = float(request.POST.get('piezasrechazoproc'))
            codigo_madera = request.POST.get('codigo_madera')
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
            volumenEntrada = calcularVolumen(codigo_madera,piezas_entrada)
            volumenCalidad = calcularVolumen(codigo_madera,piezas_calidad)
            volumenRechazo = calcularVolumen(codigo_madera,piezas_rechazo)
            form_data['volumenentrada'] = volumenEntrada
            form_data['volumencalidad'] = volumenCalidad
            form_data['volumenrechazoproc'] = volumenRechazo
            form_data['volumentotal'] = volumenCalidad + volumenRechazo

            return render(request,'previsualMOL.html',{'form_data':form_data})
    else:
        form = moldureraForm()
    return redirect('moldureraInfo')

def moldureraInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = moldureraForm(request.POST or None)
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
            
            if instance.piezasentrada > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

            instance.save()
            connection.cursor().execute("""
                UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
                """,(instance.piezascalidad, instance.codigo_madera)) 
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" - %s WHERE "codigo_madera" = %s
            """,(instance.piezasentrada,instance.codigo_madera_ant))
            

            actualizarMadera()   
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
 
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'moldureraForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

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

            return render(request,'previsualRPR.html',{'form_data':form_data})
    else:
        form = reprocesoForm()
    return redirect('reprocesoInfo')        



def reprocesoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    p = Proceso.objects.aggregate(Max('id_proceso')).get('id_proceso__max')
    if request.method == "POST":
        form = reprocesoForm(request.POST or None)
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

            if instance.piezassalida > cantidad_disponible:
                    messages.error(request, 'La cantidad de piezas ingresada es superior a la disponible')
                    return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
            instance.save()
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezas" = "piezas" + %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera))
            connection.cursor().execute("""
            UPDATE "Maderas" SET "piezasReproceso" = "piezasReproceso" - %s WHERE "codigo_madera" = %s
            """,(instance.piezassalida, instance.codigo_madera_ant))
        else:
            messages.success(request,('Error al ingresar'))
            return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas}) 
        return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})
    else:
        return render(request,'reprocesoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    