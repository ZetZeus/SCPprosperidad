from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Centrotrabajo,Area, Maquina, Maderas



def home(request):
    info_area = Centrotrabajo.objects.all
    return render(request, 'homeRema.html',{'todo': info_area})

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