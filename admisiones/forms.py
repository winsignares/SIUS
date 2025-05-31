from django import forms
from home.models.carga_academica.datos_adicionales import MateriaAprobada

class MateriaAprobadaForm(forms.ModelForm):
    class Meta:
        model = MateriaAprobada
        fields = ['fecha_inicio', 'fecha_finalizacion', 'estado_aprobacion']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_finalizacion': forms.DateInput(attrs={'type': 'date'}),
            'estado_aprobacion': forms.Select(choices=MateriaAprobada.ESTADO_OPCIONES)
        }
