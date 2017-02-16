# coding=utf-8
from django.contrib import admin

# Register your models here.

from localidad.models import Pais, Estado


class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', )

    search_fields = ['nombre']


class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'codigo', )

    search_fields = ['nombre']

admin.site.register(Pais, PaisAdmin)
admin.site.register(Estado, EstadoAdmin)
