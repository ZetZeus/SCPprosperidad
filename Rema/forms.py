from django.forms import ModelForm
from .models import Area,Centrotrabajo,Maquina,Maderas,Proceso 

class cepilladoForm(ModelForm):
    class Meta:
        model = Proceso
        field = ()