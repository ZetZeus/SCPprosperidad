from django.shortcuts import render
from django.db.models import Max

# Create your views here.
from django.http import HttpResponse
from .models import Centrotrabajo,Area, Maquina, Maderas, Proceso
from .forms import cepillado



def home(request):
    info_area = Centrotrabajo.objects.all
    return render(request, 'homeRema.html',{'todo': info_area})

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
    print(p)
    if request.method == "POST":
        form = cepillado(request.POST or None)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.id_proceso = p+1
            instance.save()    
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})

    else:
        return render(request,'cepilladoForm.html',{'inf_maquinas': info_maquinas, 'inf_maderas': info_maderas})


def trozadoInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    return render(request,'trozadoForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

def fingerInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    return render(request,'fingerForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

def moldureraInfo(request):
    info_maquinas = Maquina.objects.all
    info_maderas = Maderas.objects.all
    return render(request,'moldureraForm.html',{'maquinas': info_maquinas, 'maderas': info_maderas})

 