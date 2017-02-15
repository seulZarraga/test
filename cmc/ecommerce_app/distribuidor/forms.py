# coding=utf-8
from django import forms

from distribuidor.models import Distribuidor


class DistribuidorForm(forms.ModelForm):

    direccion_estado = forms.CharField(max_length=255, required=True)
    nombre_empresa = forms.CharField(max_length=255, required=True)

    class Meta:
        model = Distribuidor
        fields = ('direccion_cp',
                  'direccion_calle',
                  'direccion_colonia',
                  'direccion_colonia',
                  'direccion_delegacion')

    def clean_direccion_cp(self):
        """ Verifica que la direccion_cp ingresada sea valida. """
        return validate_cp(self.cleaned_data['direccion_cp'])


def validate_cp(direccion_cp):
    """ Verifica que la direccion_cp cumpla las siguientes condiciones. """
    if direccion_cp[0:2] == '00':
        raise forms.ValidationError("ingrese un número valido")

    if len(direccion_cp) is not 5:
        raise forms.ValidationError("ingrese 5 números")

    return direccion_cp
