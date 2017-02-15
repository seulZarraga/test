from __future__ import unicode_literals

from django.db import models
from django.conf import settings

# Create your models here.


class Distribuidor(models.Model):
    TIPO_CHOICES = (
        ('distribuidor_bajo', 'Distribuidor Bajo'),
        ('distribuidor_medio', 'Distribuidor Medio'),
        ('distribuidor_alto', 'Distribuidor Alto'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True)
    nombre_empresa = models.CharField(max_length=255, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    direccion_estado = models.ForeignKey('cities_light.Region', blank=True, null=True, related_name='state')
    direccion_pais = models.ForeignKey('cities_light.Country', blank=True, null=True, related_name='country')
    direccion_calle = models.CharField(max_length=255, blank=True)
    direccion_colonia = models.CharField(max_length=255, blank=True)
    direccion_delegacion = models.CharField(max_length=255, blank=True)
    direccion_cp = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=255, choices=TIPO_CHOICES, default='')
    verificado = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Distribuidores'

    def __unicode__(self):
        return self.user.first_name
