from django.shortcuts import render
from Rema.models import Area


def home(request):
    info_Area = Area.objects.all
    return render(request, 'home.html',{'todo': info_Area})

