# coding=utf-8
import datetime
import hashlib
import json
import os
import random
import logging
import string
import sys
import requests
import unicodecsv as csv
import sendgrid
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import (get_user_model, logout, authenticate, login)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.shortcuts import resolve_url
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
import requests
from decimal import Decimal
from products.models import Product, Category
from distribuidor.models import Distribuidor
from core.models import CustomUser
from core.forms import UserForm
from localidad.models import Estado
from distribuidor.forms import DistribuidorForm
from core.forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.template.loader import get_template
from django.template import Context
import cStringIO as StringIO
from xhtml2pdf import pisa
from cgi import escape


def home(request):
    context = RequestContext(request)

    if request.user.is_authenticated():

        if request.user.is_staff:
            return HttpResponseRedirect(reverse('logout'))

    return render_to_response('index.html', {"pageType": "Home Page"}, context)


def send_contact_email(request):
    context = RequestContext(request)

    sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

    name = request.POST.get('name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    message_content = request.POST.get('message')

    message = sendgrid.Mail()
    message.add_to('<ingzarragaespinosa@gmail.com>')
    message.set_html('Body')
    message.set_text('Body')
    message.set_subject('Contacto desde la pagina web')
    message.set_from('<' + email + '>')

    # You pass substitutions to your template like this
    message.add_substitution('-name-', name)
    message.add_substitution('-last_name-', last_name)
    message.add_substitution('-email-', email)
    message.add_substitution('-message-', message_content)

    # Turn on the template option
    message.add_filter('templates', 'enable', '1')

    # Tell SendGrid which template to use
    message.add_filter('templates', 'template_id', 'b805c9e2-c601-4fc1-83c9-e5eeb5026153')

    # Get back a response and status
    status, msg = sg.send(message)

    return render_to_response('contact_form_confirm.html',
                              {'pageType': 'Contact Form Confirm'},
                              context)


@staff_member_required
def batch_upload(request):

    file = request.FILES['file']

    data = csv.reader(file, encoding='latin-1')
    data.next()

    for row in data:

        category = get_object_or_404(Category, name=row[6])

        available = True

        if row[7] == '0':
            available = False

        data = {'product_name': row[1],
                'public_price': Decimal(row[2]),
                'low_distr_price': Decimal(row[3]),
                'med_distr_price': Decimal(row[4]),
                'high_distr_price': Decimal(row[5]),
                'stock': row[8],
                'sku': row[9],
                'buy_link': row[10],
                'category': category,
                'available': available,
                }

        Product.objects.update_or_create(pk=None if row[0] == '' else int(row[0]), defaults=data)

        if row[0] != '' and not Product.objects.filter(pk=int(row[0])).exists():
            Product.objects.get_or_create(pk=int(row[0]), defaults=data)

    file.close()

    products = Product.objects.all()

    for product in products:
        product.create_slug
        product.save()

    return HttpResponseRedirect(reverse("admin:index"))


def search(request, **kwargs):
    """ Redirige al catalogo correspondiente considerando la url. """
    search_type = request.get_full_path()

    user_id = ''
    distrType = ''
    distribuidor = ''

    if len(kwargs) == 1:
        user_id = kwargs['user_id']
        distribuidor = get_object_or_404(Distribuidor, user=get_object_or_404(CustomUser, pk=user_id))
        distrType = distribuidor.tipo
    else:
        distribuidor = ''

    if "/products/" in search_type:
        search_type = "products"

    return render_to_response(
        "products/product_search.html", {'search_type': search_type,
                                         'distrType': distrType,
                                         'distribuidor': distribuidor,
                                         'pageType': search_type.capitalize() + ' Catalog '
                                         'Page'}, context_instance=RequestContext(request))


@ensure_csrf_cookie
def register(request):
    context = RequestContext(request)

    if request.user.is_authenticated():

        if request.user.is_staff:
            return HttpResponseRedirect(reverse('logout'))

        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)

        distribuidor_form = DistribuidorForm(data=request.POST)

        if user_form.is_valid() and distribuidor_form.is_valid():

            # q show con esto
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt + user_form.cleaned_data['email']).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            try:

                user = user_form.save()
                user.set_password(user.password)
                user.activation_key = activation_key
                user.key_expires = key_expires
                user.save()
                distribuidor = Distribuidor(user=user)
                distribuidor.nombre_empresa = distribuidor_form.cleaned_data['nombre_empresa']
                distribuidor.direccion_estado = Estado.objects.get(pk=distribuidor_form.data.get('direccion_estado'))
                distribuidor.direccion_cp = distribuidor_form.cleaned_data['direccion_cp']
                distribuidor.save()

                # send_welcome_email('https://' + request.get_host() + reverse('confirm', kwargs={'activation_key': activation_key}), distribuidor)

                # register_user_mail(request, distribuidor)

                return render_to_response('core/register_success.html',
                                          {'pageType': 'Registro Exitoso'})

            except Exception as e:
                print e
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                user_form = UserForm()

                logger = logging.getLogger('debug')
                logger.info(e)

        else:
            logger = logging.getLogger('debug')
            logger.info(user_form.errors)
            print user_form.errors
            print distribuidor_form.errors
            print logger.info(user_form.errors)

    else:
        user_form = UserForm()

    states = Estado.objects.all()

    return render_to_response(
        'login.html',
        {'user_form': user_form,
         'states': states,
         "pageType": "Login Page", }, context
    )


@ensure_csrf_cookie
def user_login(request):
    context = RequestContext(request)

    states = Estado.objects.all()

    if request.user.is_authenticated():

        usuario = CustomUser.objects.get(pk=request.user.pk)

        if usuario.is_staff:
            return HttpResponseRedirect(reverse('logout'))

        distribuidor = Distribuidor.objects.filter(user=usuario)

        if distribuidor.exists():

            return HttpResponseRedirect(reverse('distribuidor:distr_profile', kwargs={'user_id': usuario.pk}))

        else:

            return HttpResponseRedirect(reverse('logout'))

    if request.method == 'POST':

        try:

            email = request.POST['email']
            password = request.POST['password']

            usuario = authenticate(email=email, password=password)

            distribuidor = get_object_or_404(Distribuidor, user=usuario)

            if usuario is not None and usuario.is_active and distribuidor.verificado == True:

                login(request, usuario)

                if 'remember_me' in request.POST:
                    request.session.set_expiry(2419200)  # 4 semanas

                return HttpResponseRedirect(reverse('distribuidor:distr_profile', kwargs={'user_id': usuario.pk}))

            else:
                # Bad login details were provided. So we can't log the usuario in.
                print "Invalid login details: {0}, {1}".format(email, password)
                # return HttpResponse("Invalid login details supplied.")
                return HttpResponseRedirect(reverse('logout'))

        except Exception as e:

            print e

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:

        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('login.html',
                                  {'pageType': 'Login Page',
                                   'states': states,
                                   },
                                  context)

    states = Estado.objects.all()
    return render_to_response('login.html',
                              {'pageType': 'Login Page',
                               'states': states}, context)


@login_required
def user_logout(request):
    # analytics.track(request.user.pk, 'Logged Out')

    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('login'))


@csrf_protect
def check_user(request):
    """Valida que el mail del usuario no se repita."""
    success = True

    if request.method == 'POST':

        email = request.POST.get('email')

        user = CustomUser.objects.filter(email__exact=email)

        if user.exists() and user[0].email != request.user.email:
            success = False
            print 'algo'

        return HttpResponse(json.dumps({'valid': success}), content_type="application/json")


@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=CustomPasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None,
                   html_email_template_name=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)

    if request.user.is_authenticated():

        if request.user.is_staff:
            return HttpResponseRedirect(reverse('logout'))

        HttpResponseRedirect(reverse('login'))

    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'pageType': 'Reset Form',
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=CustomSetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    usermodel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = usermodel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, usermodel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Ingresa nueva clave')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Error al resetar clave')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
        'pageType': 'Reset Complete',
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@csrf_protect
def confirm(request, activation_key):
    try:

        user = get_object_or_404(CustomUser, activation_key=activation_key)

        if user.key_expires < timezone.now():
            return render_to_response('core/confirm_expired.html', {'activation_key': activation_key})

        user.has_verified_email = True
        user.save()

        return render_to_response('core/confirm_success.html')

    except Exception as e:
        print type(e)
        print e.args
        print e

        return render_to_response('core/confirm_error.html')


@csrf_protect
def reconfirm(request, activation_key):
    try:

        user = get_object_or_404(CustomUser, activation_key=activation_key)

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key_local = hashlib.sha1(salt + user.email).hexdigest()
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        user.activation_key = activation_key_local
        user.key_expires = key_expires
        user.save()

        """
        send_welcome_email(
            request.build_absolute_uri(reverse('confirm', kwargs={'activation_key': user.activation_key})),
            request.build_absolute_uri(reverse('instrumento:instrumento_login')),
            user.email)
        """

        return render_to_response('core/reconfirm_success.html')

    except Exception as e:
        print type(e)
        print e.args
        print e

        return render_to_response('core/confirm_error.html')


def send_welcome_email(url, distribuidor):

    sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

    url = url

    message = sendgrid.Mail()
    message.add_to(' <' + distribuidor.user.email + '>')
    message.set_html('Body')
    message.set_text('Body')
    message.set_subject('Verificar correo')
    message.set_from('CMC <ingzarragaespinosa@gmail.com>')

    # You pass substitutions to your template like this
    message.add_substitution('-first_name-', distribuidor.user.first_name)
    message.add_substitution('-last_name-', distribuidor.user.last_name)
    message.add_substitution('-url-', url)

    # Turn on the template option
    message.add_filter('templates', 'enable', '1')

    # Tell SendGrid which template to use
    message.add_filter('templates', 'template_id', '6a5fe8fd-21bd-482c-ae23-eb1b75b2f0ca')

    # Get back a response and status
    status, msg = sg.send(message)


def register_user_mail(request, distribuidor):

    sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

    message = sendgrid.Mail()
    message.add_to(' <ingzarragaespinosa@gmail.com>')
    message.set_html('Body')
    message.set_text('Body')
    message.set_subject('Un nuevo usiario quiere ser distribuidor')
    message.set_from(' <' + distribuidor.user.email + '>')

    # You pass substitutions to your template like this
    message.add_substitution('-first_name-', distribuidor.user.first_name)
    message.add_substitution('-last_name-', distribuidor.user.last_name)
    message.add_substitution('-telephone-', distribuidor.user.telephone)
    message.add_substitution('-email-', distribuidor.user.email)

    # Turn on the template option
    message.add_filter('templates', 'enable', '1')

    # Tell SendGrid which template to use
    message.add_filter('templates', 'template_id', '5e91fb1a-c2fd-4c45-99a6-49fe0dcaee71')

    # Get back a response and status
    status, msg = sg.send(message)


@login_required
def diff_user(request, user_id):
    """ Verifica que no haya dos usuarios con el mismo id. """
    if str(request.user.pk) != str(user_id):
        return True
    else:
        return False


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))
