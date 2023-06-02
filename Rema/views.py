from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Centrotrabajo,Area


def index(request):
    return HttpResponse("Hello, world. You're at the Rema index.")

def home(request):
    info_area = Centrotrabajo.objects.all
    return render(request, 'homeAreas.html',{'todo': info_area})