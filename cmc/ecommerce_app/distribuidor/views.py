# coding=utf-8
from django.shortcuts import render, render_to_response, get_object_or_404

from distribuidor.models import Distribuidor

from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect

from django.core.urlresolvers import reverse

from products.models import Product

from core.views import diff_user, render_to_pdf

from core.models import CustomUser

from distribuidor.forms import DistribuidorForm

from localidad.models import Estado

from core.forms import UserForm


@login_required
def home(request):
    return HttpResponseRedirect(reverse('login'))


@login_required
def distribuidor_profile(request, user_id):
    context = RequestContext(request)

    distribuidor = get_object_or_404(Distribuidor, user=get_object_or_404(CustomUser, pk=user_id))

    distrType = distribuidor.tipo

    if diff_user(request, distribuidor.user.pk):
        return HttpResponseRedirect(reverse('login'))

    return render_to_response('distr/distribuidor_profile.html',
                              {'pageType': 'Distribuidor Profile Page',
                               'distrType': distrType,
                               'distribuidor': distribuidor, }, context)


@login_required
def edit_profile(request, user_id):
    context = RequestContext(request)

    distribuidor = get_object_or_404(Distribuidor, user=get_object_or_404(CustomUser, pk=user_id))

    states = Estado.objects.all()

    if diff_user(request, distribuidor.user.pk):
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':

        distribuidor_form = DistribuidorForm(request.POST, request.FILES, instance=distribuidor)

        user_form = UserForm(request.POST, request.FILES, instance=distribuidor.user)

        if distribuidor_form.is_valid() and user_form.is_valid():

            distribuidor.user.first_name = user_form.cleaned_data['first_name']

            distribuidor.user.second_last_name = user_form.cleaned_data['second_last_name']

            distribuidor.user.last_name = user_form.cleaned_data['last_name']

            distribuidor.user.email = user_form.cleaned_data['email']

            distribuidor.nombre_empresa = distribuidor_form.cleaned_data['nombre_empresa']

            distribuidor.direccion_estado = Estado.objects.get(pk=distribuidor_form.data.get('direccion_estado'))

            distribuidor.direccion_calle = distribuidor_form.cleaned_data['direccion_calle']

            distribuidor.direccion_colonia = distribuidor_form.cleaned_data['direccion_colonia']

            distribuidor.direccion_delegacion = distribuidor_form.cleaned_data['direccion_delegacion']

            distribuidor.direccion_cp = distribuidor_form.cleaned_data['direccion_cp']

            distribuidor.save()
            distribuidor.user.save()

            return HttpResponseRedirect(reverse('distribuidor:distr_profile', kwargs={'user_id': user_id}))
        else:
            print distribuidor_form.errors
            print user_form.errors

    return render_to_response('distr/edit_profile.html',
                              {'distribuidor': distribuidor,
                               'states': states}, context)


@login_required
def download_prices(request, user_id):

    products = Product.objects.all().order_by('category')

    distribuidor = get_object_or_404(Distribuidor, user=get_object_or_404(CustomUser, pk=user_id))

    if diff_user(request, distribuidor.user.pk):
        return HttpResponseRedirect(reverse('login'))

    return render_to_pdf('pdf/prices_catalog.html',
                         {'pagesize': 'A4',
                          'products': products,
                          'distribuidor': distribuidor,
                          })
