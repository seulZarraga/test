from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Pais(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    codigo = models.CharField(max_length=2, blank=True, null=True)

    class Meta:

        verbose_name_plural = 'Paises'

    def __unicode__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    pais = models.ForeignKey('Pais')
    codigo = models.CharField(max_length=3, blank=True, null=True)

    def __unicode__(self):
        return self.nombre
