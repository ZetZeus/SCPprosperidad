from django.shortcuts import render
from Rema.models import Area


def home(request):
    info_Area = Area.objects.all
    return render(request, 'home.html',{'todo': info_Area})

def join_area(request, id):
     dataArea = Area.objects.get(id=id)
     return render (request, 'homeAreas.html', {'datosArea':dataArea})