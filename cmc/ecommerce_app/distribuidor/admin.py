# coding=utf-8
from django.contrib import admin

from distribuidor.models import Distribuidor
# Register your models here.


class DistribuidorAdmin(admin.ModelAdmin):
    list_display = ('get_user_name',
                    'user',
                    'tipo',
                    'direccion_estado',)

    def get_user_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

admin.site.register(Distribuidor, DistribuidorAdmin)
