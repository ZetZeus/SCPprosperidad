from django.shortcuts import render
from paginaAreas.models import Area


def home(request):
    info_ct = Area.objects.all
    return render(request, 'home.html',{'todo': info_ct})