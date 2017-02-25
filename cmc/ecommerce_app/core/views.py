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

    print products

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
                                         'Page'},
                                         context_instance=RequestContext(request))


@csrf_protect
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


@csrf_protect
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

                print distribuidor.nombre_empresa
                print distribuidor.verificado

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

    print sg.send(message)


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


# def get_cart(request):
#     cart = request.session.get('cart', {})

#     products = []
#     cart_total = 0

#     for pid, qty in cart.items():
#         product = get_object_or_404(Product, pk=pid)

#         setattr(product, 'qty', qty)

#         products.append(product)
#         cart_total += product.total * int(qty)

#     return {'products': products, 'cart_total': cart_total}


# def get_saved(request):
#     saved = request.session.get('saved', {})

#     products = []

#     for pid, qty in saved.items():
#         product = get_object_or_404(Product, pk=pid)

#         products.append(product)

#     return products


# def get_coupon(request):
#     coupon = request.session.get('coupon', {})

#     coupon_name = ''
#     coupon_discount = ''

#     for x in coupon:
#         coupon_name = x
#         coupon_discount = coupon[x]

#     return {'coupon_name': coupon_name, 'coupon_discount': coupon_discount}


# def cart(request):
#     context = RequestContext(request)

#     coupon_discount = 0

#     if get_coupon(request)['coupon_discount'] != '':
#         coupon_discount = int(get_coupon(request)['coupon_discount'])


#     #coupon_apply_to_cart(request)

#     return render_to_response('cart.html',
#                               {'products': get_cart(request)['products'], 'saved_products': get_saved(request),
#                                'cart_total': get_cart(request)['cart_total'] - coupon_discount,
#                                'coupon_name': get_coupon(request)['coupon_name'],
#                                'coupon_discount': get_coupon(request)['coupon_discount'],
#                                'invalid_coupon': request.session.get('invalid_coupon'),
#                                'pageType': 'Cart Page', "main_categories": get_main_categories()}, context)


# def add_to_cart(request, product_id, quantity):
#     product = get_object_or_404(Product, pk=product_id)

#     if product.can_sell():
#         cart = request.session.get('cart', {})

#         cart[product_id] = quantity

#         request.session['cart'] = cart

#     return HttpResponseRedirect(reverse('cart'))
#     # rest of the view


# def add_to_cart_one(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)

#     if product.can_sell():

#         cart = request.session.get('cart', {})

#         if product_id in cart:

#             cart[product_id] = str(int(cart[product_id]) + 1)

#         else:

#             cart[product_id] = 1

#         request.session['cart'] = cart

#     return HttpResponseRedirect(reverse('cart'))
#     # rest of the view


# def remove_from_cart(request, product_id):
#     cart = request.session.get('cart', {})
#     del cart[product_id]
#     request.session['cart'] = cart

#     return HttpResponseRedirect(reverse('cart'))
#     # rest of the view


# def clear_cart(request):
#     del request.session['cart']


# def add_save_for_later(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)

#     if product.can_sell():
#         saved = request.session.get('saved', {})

#         cart = request.session.get('cart', {})

#         saved[product_id] = cart[product_id]

#         request.session['saved'] = saved

#     return HttpResponseRedirect(reverse('remove_from_cart', kwargs={'product_id': product_id}))


# def move_saved_to_cart(request, product_id):
#     # remove from saved
#     saved = request.session.get('saved', {})
#     del saved[product_id]
#     request.session['saved'] = saved

#     return HttpResponseRedirect(reverse('add_to_cart_one', kwargs={'product_id': product_id}))


# def privacy(request):
#     context = RequestContext(request)

#     return render_to_response('privacidad.html', {'pageType': 'Privacy Page', "main_categories": get_main_categories()},
#                               context)


# def terms(request):
#     context = RequestContext(request)

#     return render_to_response('terminos.html', {'pageType': 'Terms Page', "main_categories": get_main_categories()},
#                               context)





# @login_required
# def checkout(request):
#     context = RequestContext(request)

#     client = get_object_or_404(Client, user=request.user)

#     countries = Country.objects.all()

#     cart = request.session.get('cart', {})

#     payment_methods = PaymentMethod.objects.filter(active=True)

#     p_list = []

#     for product in get_cart(request)['products']:
#         p_list.append({"id": str(product.pk), "q": product.qty})

#     custom = str(client.pk) + "&" + str(p_list)

#     paypal_dict = {
#         "business": settings.PAYPAL_EMAIL,
#         "notify_url": settings.PAYPAL_NOTIFY_URL,
#         "return_url": settings.PAYPAL_RETURN_URL,
#         # todo cambiar esto por una url de verdad
#         "cancel_return": "https://www.example.com/your-cancel-location/",
#         "txn_type": "cart",
#         "cmd": "_cart",
#         "upload": "1",
#         "num_cart_items": len(get_cart(request)['products']),
#         "custom": custom,
#     }

#     counter = 1

#     for product in get_cart(request)['products']:
#         paypal_dict['item_name_' + str(counter)] = product.name
#         paypal_dict['item_number_' + str(counter)] = product.pk
#         paypal_dict['quantity_' + str(counter)] = product.qty
#         paypal_dict['amount_' + str(counter)] = product.total

#         counter += 1

#     # Create the instance.
#     form = PayPalPaymentsForm(initial=paypal_dict)

#     coupon_discount = 0

#     if get_coupon(request)['coupon_discount'] != '':
#         coupon_discount = int(get_coupon(request)['coupon_discount'])

#     if cart:
#         return render_to_response('checkout.html', {'countries': countries,
#                                                     'paypal': form,
#                                                     'cart_products': get_cart(request)['products'],
#                                                     'cart_sub_total': get_cart(request)['cart_total'],
#                                                     'cart_total': get_cart(request)['cart_total'] - coupon_discount,
#                                                     'payments': payment_methods,
#                                                     'shipping_addresses': client.shipping_address,
#                                                     'coupon_name': get_coupon(request)['coupon_name'],
#                                                     'coupon_discount': get_coupon(request)['coupon_discount'],
#                                                     'pageType': 'Checkout Page',
#                                                     'main_categories': get_main_categories()}, context)
#     else:
#         return HttpResponseRedirect(reverse('cart'))


# @login_required
# def success(request, order_id):
#     context = RequestContext(request)

#     order = get_object_or_404(Order, pk=order_id)

#     products = OrderHasProducts.objects.filter(order=order)

#     if request.user == order.client.user:

#         return render_to_response('success.html', {'products': products, 'order': order, 'pageType': 'Success Page',
#                                                    "main_categories": get_main_categories()},
#                                   context)

#     else:

#         return HttpResponseRedirect(reverse('login'))


# @require_GET
# def paypal_success(request):
#     pdt_obj, failed = process_pdt(request)

#     context = {"failed": failed, "pdt_obj": pdt_obj}

#     if not failed:

#         # WARNING!
#         # Check that the receiver email is the same we previously
#         # set on the business field request. (The user could tamper
#         # with those fields on payment form before send it to PayPal)

#         if pdt_obj.receiver_email == settings.PAYPAL_EMAIL:

#             extra_info = json.loads(pdt_obj.custom)

#             client = get_object_or_404(Client, pk=extra_info['client_id'])

#             shipping_address = get_object_or_404(Address, pk=extra_info['shipping_address'])
#             shipping_method = get_object_or_404(ShippingMethod, pk=extra_info['shipping_method'])
#             payment_method = get_object_or_404(PaymentMethod, pk=extra_info['payment_method'])

#             order = Order.objects.create(client=client,
#                                          shipping_address=shipping_address,
#                                          shipping_method=shipping_method,
#                                          payment_method=payment_method,
#                                          paypal_email=pdt_obj.payer_email,
#                                          status='approved')

#             for product in eval(extra_info["products"]):
#                 p = get_object_or_404(Product, pk=product['id'])

#                 OrderHasProducts.objects.create(order=order, product=p, quantity=product['q'])

#             clear_cart(request)

#             order_products = OrderHasProducts.objects.filter(order=order)

#             context = RequestContext(request)

#             send_success_email(client, order)
#             send_purchase_email_to_mexeart(client, order)
#             send_purchase_email_to_sellers(client, order)

#             return render_to_response('success.html',
#                                       {'products': order_products, 'order': order, 'pageType': 'Success Page',
#                                        "main_categories": get_main_categories()},
#                                       context)

#     # todo hacer template de orden no valida
#     return render(request, 'my_non_valid_payment_template', context)


# def get_main_categories():
#     return Category1.objects.all()


# @csrf_protect
# def check_user(request):
#     """Valida que el mail del usuario no se repita."""
#     success = True

#     if request.method == 'POST':

#         email = request.POST.get('email')

#         user = CustomUser.objects.filter(email__exact=email)

#         if user.exists():

#             if request.user.is_authenticated():

#                 if user[0].email != request.user.email:
#                     success = False

#             else:

#                 success = False

#         return HttpResponse(json.dumps({'valid': success}), content_type="application/json")


# def send_success_email(client, order):
#     sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

#     message = sendgrid.Mail()
#     message.add_to(str(client.user.get_full_name()) + ' <' + client.user.email + '>')
#     message.set_html('Body')
#     message.set_text('Body')
#     message.set_subject('Example')
#     message.set_from('Mex E-Art <contacto@mexeart.com>')

#     order_items_html = ""

#     items = OrderHasProducts.objects.filter(order=order)

#     for item in items:
#         order_items_html += '<tr><td>' + str(item.product.name) + '</td><td>' + str(item.quantity) + '</td><td>' + str(
#             item.product.total * item.quantity) + '</td></tr>'

#     order_items_html = '<table><tr><td>Product</td><td>Quantity</td><td>Total</td></tr>' + order_items_html + '</table>'

#     # You pass substitutions to your template like this
#     message.add_substitution('-first_name-', client.user.first_name)
#     message.add_substitution('-order_number-', order.order_number)
#     message.add_substitution('-order_status-', order.status)
#     message.add_substitution('-order_address-', order.shipping_address.full_address)
#     message.add_substitution('-order_items-', order_items_html)
#     message.add_substitution('-order_subtotal-', order.order_subtotal)
#     message.add_substitution('-order_shipping-', order.shipping_method.cost)
#     message.add_substitution('-order_total-', order.order_total)

#     # Turn on the template option
#     message.add_filter('templates', 'enable', '1')

#     # Tell SendGrid which template to use
#     message.add_filter('templates', 'template_id', '86cefb43-c0f1-42fa-bc9f-5afae02c4a30')

#     # Get back a response and status
#     status, msg = sg.send(message)


# def send_purchase_email_to_mexeart(client, order):
#     sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

#     message = sendgrid.Mail()
#     message.add_to('Mex E-Art <contacto@mexeart.com>')
#     message.set_html('Body')
#     message.set_text('Body')
#     message.set_subject('Example')
#     message.set_from('Mex E-Art <contacto@mexeart.com>')

#     order_items_html = ""

#     items = OrderHasProducts.objects.filter(order=order)

#     for item in items:
#         order_items_html += '<tr><td>' + str(item.product.name) + '</td><td>' + str(item.quantity) + '</td><td>' + str(
#             item.product.total * item.quantity) + '</td></tr>'

#     order_items_html = '<table><tr><td>Product</td><td>Quantity</td><td>Total</td></tr>' + order_items_html + '</table>'

#     # You pass substitutions to your template like this
#     message.add_substitution('-first_name-', client.user.first_name)
#     message.add_substitution('-order_number-', order.order_number)
#     message.add_substitution('-order_status-', order.status)
#     message.add_substitution('-order_address-', order.shipping_address.full_address)
#     message.add_substitution('-order_items-', order_items_html)
#     message.add_substitution('-order_subtotal-', order.order_subtotal)
#     message.add_substitution('-order_shipping-', order.shipping_method.cost)
#     message.add_substitution('-order_total-', order.order_total)

#     # Turn on the template option
#     message.add_filter('templates', 'enable', '1')

#     # Tell SendGrid which template to use
#     message.add_filter('templates', 'template_id', '9ba7bc6d-53f3-4832-9d3a-1fb5573ac4bc')

#     # Get back a response and status
#     status, msg = sg.send(message)


# def send_purchase_email_to_sellers(client, order):
#     sellers = OrderHasProducts.objects.filter(order=order).values('product__seller').annotate(
#         dcount=Count('product__seller'))

#     sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

#     for seller in sellers:

#         seller_obj = Seller.objects.get(pk=seller['product__seller'])

#         message = sendgrid.Mail()
#         message.add_to(str(seller_obj.user.get_full_name()) + ' <' + str(seller_obj.user.email) + '>')
#         message.set_html('Body')
#         message.set_text('Body')
#         message.set_subject('Example')
#         message.set_from('Mex E-Art <contacto@mexeart.com>')

#         order_items_html = ""

#         seller_obj = Seller.objects.get(pk=seller['product__seller'])

#         items = OrderHasProducts.objects.filter(order__id=33, product__seller=seller_obj)

#         for item in items:
#             order_items_html += '<tr><td>' + str(item.product.name) + '</td><td>' + str(
#                 item.quantity) + '</td><td>' + str(
#                 item.product.total * item.quantity) + '</td></tr>'

#         order_items_html = '<table><tr><td>Product</td><td>Quantity</td><td>Total</td></tr>' + order_items_html + '</table>'

#         # You pass substitutions to your template like this
#         message.add_substitution('-first_name-', client.user.first_name)
#         message.add_substitution('-order_number-', order.order_number)
#         message.add_substitution('-order_items-', order_items_html)

#         # Turn on the template option
#         message.add_filter('templates', 'enable', '1')

#         # Tell SendGrid which template to use
#         message.add_filter('templates', 'template_id', '2d449d7a-3ad4-4ff0-942f-e667cacc477e')

#         # Get back a response and status
#         status, msg = sg.send(message)


# @require_POST
# @csrf_protect
# def send_become_seller_email(request):
#     context = RequestContext(request)

#     sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

#     full_name = request.POST.get('full_name')
#     email = request.POST.get('email')
#     phone = request.POST.get('phone')
#     company_name = request.POST.get('company_name')
#     address = request.POST.get('address')
#     business = request.POST.get('business')
#     products = request.POST.get('products')
#     message_content = request.POST.get('message')

#     if grecaptcha_verify(request) and full_name != '' and email != '' and phone != '':

#         message = sendgrid.Mail()
#         message.add_to('Mex E-Art <contacto@mexeart.com>')
#         message.set_html('Body')
#         message.set_text('Body')
#         message.set_subject('Example')
#         message.set_from(full_name + ' <' + email + '>')

#         # You pass substitutions to your template like this
#         message.add_substitution('-full_name-', full_name)
#         message.add_substitution('-email-', email)
#         message.add_substitution('-phone-', phone)
#         message.add_substitution('-company_name-', company_name)
#         message.add_substitution('-address-', address)
#         message.add_substitution('-business-', business)
#         message.add_substitution('-products-', products)
#         message.add_substitution('-message-', message_content)

#         # Turn on the template option
#         message.add_filter('templates', 'enable', '1')

#         # Tell SendGrid which template to use
#         message.add_filter('templates', 'template_id', '28c2b181-dde7-4e5e-86f8-6374049320e2')

#         # Get back a response and status
#         status, msg = sg.send(message)

#         return render_to_response('contact_form_confirm.html',
#                                   {'pageType': 'Contact Form Confirm', "main_categories": get_main_categories()},
#                                   context)

#     else:

#         return HttpResponseRedirect(reverse('become_seller'))


# @require_POST
# @csrf_protect
# def send_corporate_sale_email(request):
#     context = RequestContext(request)

#     sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

#     full_name = request.POST.get('full_name')
#     email = request.POST.get('email')
#     phone = request.POST.get('phone')
#     company_name = request.POST.get('company_name')
#     address = request.POST.get('address')
#     message_content = request.POST.get('message')

#     if grecaptcha_verify(request) and full_name != '' and email != '' and phone != '':

#         message = sendgrid.Mail()
#         message.add_to('Mex E-Art <contacto@mexeart.com>')
#         message.set_html('Body')
#         message.set_text('Body')
#         message.set_subject('Example')
#         message.set_from(full_name + ' <' + email + '>')

#         # You pass substitutions to your template like this
#         message.add_substitution('-full_name-', full_name)
#         message.add_substitution('-email-', email)
#         message.add_substitution('-phone-', phone)
#         message.add_substitution('-company_name-', company_name)
#         message.add_substitution('-address-', address)
#         message.add_substitution('-message-', message_content)

#         # Turn on the template option
#         message.add_filter('templates', 'enable', '1')

#         # Tell SendGrid which template to use
#         message.add_filter('templates', 'template_id', 'd74c9aa4-0046-44ff-a01c-2a5184ad9f2b')

#         # Get back a response and status
#         status, msg = sg.send(message)

#         return render_to_response('contact_form_confirm.html',
#                                   {'pageType': 'Contact Form Confirm', "main_categories": get_main_categories()},
#                                   context)

#     else:

#         return HttpResponseRedirect(reverse('corporate_sales'))





# @require_POST
# def grecaptcha_verify(request):
#     captcha_rs = request.POST.get('g-recaptcha-response')

#     url = "https://www.google.com/recaptcha/api/siteverify"

#     params = {
#         'secret': settings.RECAPTCHA_SECRET_KEY,
#         'response': captcha_rs,
#         'remoteip': get_client_ip(request),
#     }

#     verify_rs = requests.post(url, params=params, verify=True)

#     verify_rs = verify_rs.json()

#     return verify_rs.get("success")


# def get_client_ip(request):
#     """Returns the IP of the request, accounting for the possibility of being
#     behind a proxy.
#     """
#     ip = request.META.get("HTTP_X_FORWARDED_FOR", None)

#     if ip:
#         # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
#         ip = ip.split(", ")[0]

#     else:
#         ip = request.META.get("REMOTE_ADDR", "")

#     return ip


# def ups_quote(cart, to_address):

#     ups_services = [
#         ('01', 'Next Day Air'),
#         ('02', '2nd Day Air'),
#         ('03', 'Ground'),
#         ('12', '3 Day Select'),
#         ('13', 'Next Day Air Saver'),
#         ('14', 'UPS Next Day Air Early'),
#         ('59', '2nd Day Air A.M.'),
#         ('07', 'Worldwide Express'),
#         ('08', 'Worldwide Expedited'),
#         ('11', 'Standard'),
#         ('54', 'Worldwide Express Plus'),
#         ('65', 'Saver'),
#         ('96', 'UPS Worldwide Express Freight'),
#     ]

#     ups_services = dict(ups_services)

#     request_obj = {
#         "RateRequest": {
#             "Request": {
#                 "RequestOption": "Shop",
#                 "TransactionReference": {
#                     "CustomerContext": "Your Customer Context"
#                 }
#             },
#             "Shipment": {
#                 "Package": {
#                     "Dimensions": {
#                         "Height": "3",
#                         "Length": "5",
#                         "UnitOfMeasurement": {
#                             "Code": "CM",
#                         },
#                         "Width": "4"
#                     },
#                     "PackageWeight": {
#                         "UnitOfMeasurement": {
#                             "Code": "KGS",
#                         },
#                         "Weight": "1"
#                     },
#                     "PackagingType": {
#                         "Code": "02", # cual usar
#                     }
#                 },
#                 "ShipFrom": {
#                     "Address": {
#                         "AddressLine": [
#                             "Address Line ",
#                             "Address Line "
#                         ],
#                         "City": "City",
#                         "CountryCode": settings.DHL_COUNTRY_CODE,
#                         "PostalCode": settings.DHL_ORIGIN_CP,
#                         #"StateProvinceCode": "NJ"
#                     },
#                     "Name": "MEXICAN CULTURE TRADE AND COMMERCE"
#                 },
#                 "ShipTo": {
#                     "Address": {
#                         "AddressLine": [
#                             to_address.street,
#                             to_address.street2
#                         ],
#                         "City": to_address.city,
#                         "CountryCode": to_address.country.code2,
#                         "PostalCode": to_address.zip_code,
#                         #"StateProvinceCode": to_address.state.code2
#                     },
#                     "Name": to_address.first_name + " " + to_address.last_name
#                 },
#                 "ShipmentRatingOptions": {
#                     "NegotiatedRatesIndicator": ""
#                 },
#                 "Shipper": {
#                     "Address": {
#                         "AddressLine": [
#                             "Address Line ",
#                             "Address Line ",
#                             "Address Line "
#                         ],
#                         "City": "Boca Raton",
#                         "CountryCode": settings.DHL_COUNTRY_CODE,
#                         "PostalCode": settings.DHL_ORIGIN_CP,
#                         #"StateProvinceCode":
#                     },
#                     "Name": "MEXICAN CULTURE TRADE AND COMMERCE",
#                     "ShipperNumber": "MEXICANCUPS"
#                 }
#             }
#         },
#         "UPSSecurity": {
#             "ServiceAccessToken": {
#                 "AccessLicenseNumber": settings.UPS_ACCESS_TOKEN
#             },
#             "UsernameToken": {
#                 "Password": settings.UPS_PWD,
#                 "Username": settings.UPS_USER
#             }
#         }
#     }

#     r = requests.post(settings.UPS_URL, data=json.dumps(request_obj))

#     response = json.loads(r.content)

#     print response

#     services = []

#     ups_method_pk = ShippingMethod.objects.get(name='UPS').pk

#     for service in response['RateResponse']['RatedShipment']:

#         service = {'method_id': ups_method_pk,
#                    'service_code': service['Service']['Code'],
#                    'service_name': ups_services[service['Service']['Code']],
#                    'service_delivery_date': '',
#                    'service_cost': service['TotalCharges']['MonetaryValue']
#                    }

#         services.append(service)

#     return services


# def dhl_quote(cart, to_address):
#     P = 'http://www.dhl.com'

#     XSI = 'http://www.w3.org/2001/XMLSchema-instance'

#     # create XML

#     root = Element(QName(P, 'DCTRequest'),
#                    nsmap={'p': P, 'p1': 'http://www.dhl.com/datatypes', 'p2': 'http://www.dhl.com/DCTRequestdatatypes',
#                           'xsi': XSI})

#     root.attrib[QName(XSI, 'schemaLocation')] = 'http://www.dhl.com DCT-req.xsd'

#     get_quote = SubElement(root, "GetQuote")

#     request = SubElement(get_quote, "Request")

#     service_header = SubElement(request, "ServiceHeader")

#     site_id = SubElement(service_header, "SiteID")
#     site_id.text = settings.DHL_SITE_ID

#     password = SubElement(service_header, "Password")

#     password.text = settings.DHL_PASSWORD

#     from_dir = SubElement(get_quote, "From")

#     from_country_code = SubElement(from_dir, "CountryCode")
#     from_country_code.text = settings.DHL_COUNTRY_CODE

#     from_postal_code = SubElement(from_dir, "Postalcode")
#     from_postal_code.text = settings.DHL_ORIGIN_CP

#     bkg_details = SubElement(get_quote, "BkgDetails")

#     payment_country_code = SubElement(bkg_details, "PaymentCountryCode")

#     payment_country_code.text = 'MX'

#     date = SubElement(bkg_details, "Date")
#     date.text = str(datetime.date.today())

#     ready_time = SubElement(bkg_details, "ReadyTime")
#     ready_time.text = 'PT10H21M'  # duda en esta

#     dimenssion_unit = SubElement(bkg_details, "DimensionUnit")
#     dimenssion_unit.text = 'CM'

#     weight_unit = SubElement(bkg_details, "WeightUnit")
#     weight_unit.text = 'KG'

#     pieces = SubElement(bkg_details, "Pieces")

#     for product in cart['products']:

#         for x in range(0, int(product.qty)):
#             piece = SubElement(pieces, "Piece")
#             piece_id = SubElement(piece, "PieceID")
#             piece_id.text = str(product.pk)

#             piece_height = SubElement(piece, "Height")
#             piece_height.text = str(product.package_height)

#             piece_depth = SubElement(piece, "Depth")
#             piece_depth.text = str(product.package_length)

#             piece_witdth = SubElement(piece, "Width")
#             piece_witdth.text = str(product.package_width)

#             piece_weight = SubElement(piece, "Weight")
#             piece_weight.text = str(product.package_weight)

#     is_duitable = SubElement(bkg_details, "IsDutiable")
#     is_duitable.text = 'N'  # duda en esta

#     to_dir = SubElement(get_quote, "To")

#     to_country_code = SubElement(to_dir, "CountryCode")
#     to_country_code.text = to_address.country.code2
#     to_postal_code = SubElement(to_dir, "Postalcode")
#     to_postal_code.text = to_address.zip_code

#     r = requests.post(settings.DHL_URL, data=tostring(root))

#     response = fromstring(r.content)[0][1]

#     services = []

#     dhl_method_pk = ShippingMethod.objects.get(name='DHL')

#     for service in response.findall('QtdShp'):

#         if service.find('TransInd').text != 'N':
#             service = {'method_id': dhl_method_pk.pk,
#                        'service_code': service.find('GlobalProductCode').text,
#                        'service_name': service.find('ProductShortName').text,
#                        'service_delivery_date': service.find('DeliveryDate').text,
#                        'service_cost': service.find('ShippingCharge').text
#                        }

#             services.append(service)

#     return services


# def dhl_shipment_request(order):
#     order_products = OrderHasProducts.objects.filter(order=order)

#     pieces_list = []

#     max_fullfill_day = 0

#     REQ = "http://www.dhl.com"
#     XSI = "http://www.w3.org/2001/XMLSchema-instance"

#     for product in order_products:

#         if max_fullfill_day < product.product.seller.fulfillment_days:
#             max_fullfill_day = product.product.seller.fulfillment_days

#         for x in range(0, int(product.quantity)):
#             pieces_list.append(product.product)

#     # create XML
#     root = Element(QName(REQ, 'ShipmentRequest'), nsmap={'req': REQ, 'xsi': XSI})

#     root.attrib[QName(XSI, 'schemaLocation')] = 'http://www.dhl.com ship-val-global-req.xsd'

#     root.attrib['schemaVersion'] = '4.0'

#     request = SubElement(root, "Request")

#     service_header = SubElement(request, "ServiceHeader")

#     message_time = SubElement(service_header, "MessageTime")
#     message_time.text = timezone.now().strftime('%Y-%m-%dT%H:%M:%S-05:00')

#     message_reference = SubElement(service_header, "MessageReference")

#     random_reference = ''.join(random.choice(string.lowercase) for i in range(31))

#     message_reference.text = random_reference

#     site_id = SubElement(service_header, "SiteID")
#     site_id.text = settings.DHL_SITE_ID

#     password = SubElement(service_header, "Password")

#     password.text = settings.DHL_PASSWORD

#     region_code = SubElement(root, "RegionCode")
#     region_code.text = 'AM'

#     requested_pickup_time = SubElement(root, "RequestedPickupTime")
#     requested_pickup_time.text = 'Y'  # para q es esto

#     new_shipper = SubElement(root, "NewShipper")
#     new_shipper.text = 'Y'  # para q es esto

#     language_code = SubElement(root, "LanguageCode")
#     language_code.text = 'en'

#     pieces_enabled = SubElement(root, "PiecesEnabled")
#     pieces_enabled.text = 'Y'

#     billing = SubElement(root, "Billing")
#     shipper_account_number = SubElement(billing, "ShipperAccountNumber")
#     shipper_account_number.text = settings.DHL_ACCOUNT
#     shipper_payment_type = SubElement(billing, "ShippingPaymentType")
#     shipper_payment_type.text = 'S'
#     billing_account_number = SubElement(billing, "BillingAccountNumber")
#     billing_account_number.text = settings.DHL_ACCOUNT
#     duty_payment_type = SubElement(billing, "DutyPaymentType")
#     duty_payment_type.text = 'S'
#     duty_account_number = SubElement(billing, "DutyAccountNumber")
#     duty_account_number.text = settings.DHL_ACCOUNT

#     consignee = SubElement(root, "Consignee")
#     # como quitar el company name
#     # place_type = SubElement(consignee, "ResidenceOrBusiness")
#     # place_type.text = 'R'
#     company_name = SubElement(consignee, "CompanyName")
#     company_name.text = 'None'

#     address_line = SubElement(consignee, "AddressLine")
#     address_line.text = order.shipping_address.street

#     if len(order.shipping_address.street2) > 0:
#         address_line2 = SubElement(consignee, "AddressLine")
#         address_line2.text = order.shipping_address.street2

#     city = SubElement(consignee, "City")
#     city.text = order.shipping_address.state.name
#     division = SubElement(consignee, "Division")
#     division.text = order.shipping_address.city
#     postal_code = SubElement(consignee, "PostalCode")
#     postal_code.text = order.shipping_address.zip_code
#     country_code = SubElement(consignee, "CountryCode")
#     country_code.text = order.shipping_address.country.code2
#     country_name = SubElement(consignee, "CountryName")
#     country_name.text = order.shipping_address.country.name

#     contact = SubElement(consignee, "Contact")
#     person_name = SubElement(contact, "PersonName")
#     person_name.text = order.shipping_address.first_name + " " + order.shipping_address.last_name
#     phone_number = SubElement(contact, "PhoneNumber")
#     phone_number.text = order.client.user.telephone
#     contact_email = SubElement(contact, "Email")
#     contact_email.text = order.client.user.email

#     duitable = SubElement(root, "Dutiable")
#     declared_value = SubElement(duitable, "DeclaredValue")
#     declared_value.text = str(order.order_subtotal)
#     declared_currency = SubElement(duitable, "DeclaredCurrency")
#     declared_currency.text = 'USD'

#     reference = SubElement(root, "Reference")
#     reference_id = SubElement(reference, "ReferenceID")
#     reference_id.text = str(order.order_number)

#     shipment_details = SubElement(root, "ShipmentDetails")
#     number_of_pieces = SubElement(shipment_details, "NumberOfPieces")
#     number_of_pieces.text = str(len(pieces_list))

#     pieces = SubElement(shipment_details, "Pieces")

#     total_weight = 0

#     for p in pieces_list:
#         piece = SubElement(pieces, "Piece")

#         piece_id = SubElement(piece, "PieceID")
#         piece_id.text = str(p.pk)

#         piece_pkg_type = SubElement(piece, "PackageType")
#         piece_pkg_type.text = 'YP'  # duda con tipos de paquetes

#         piece_weight = SubElement(piece, "Weight")
#         piece_weight.text = str(p.package_weight)

#         piece_dimweight = SubElement(piece, "DimWeight")
#         piece_dimweight.text = str(p.shipping_weight())

#         piece_witdth = SubElement(piece, "Width")
#         piece_witdth.text = str(p.package_width)

#         piece_height = SubElement(piece, "Height")
#         piece_height.text = str(p.package_height)

#         piece_depth = SubElement(piece, "Depth")
#         piece_depth.text = str(p.package_length)

#         total_weight += p.package_weight

#     weight = SubElement(shipment_details, "Weight")
#     weight.text = str(total_weight)
#     weight_unit = SubElement(shipment_details, "WeightUnit")
#     weight_unit.text = 'K'

#     global_product_code = SubElement(shipment_details, "GlobalProductCode")
#     global_product_code.text = order.dhl_shipping_service_code
#     shipping_date = SubElement(shipment_details, "Date")

#     shipping_date.text = str(
#         datetime.date.today() + datetime.timedelta(days=int(settings.DHL_FULFIILL_DAYS) + max_fullfill_day))

#     contents = SubElement(shipment_details, "Contents")
#     contents.text = 'Fragile Decoration and Art Products'

#     d_d = SubElement(shipment_details, "DoorTo")
#     d_d.text = 'DD'

#     dimension_unit = SubElement(shipment_details, "DimensionUnit")
#     dimension_unit.text = 'C'

#     insured_amount = SubElement(shipment_details, "InsuredAmount")
#     insured_amount.text = str(order.order_subtotal)  # preguntar por eso

#     package_type = SubElement(shipment_details, "PackageType")
#     package_type.text = 'YP'  # preguntando eso

#     is_duitable = SubElement(shipment_details, "IsDutiable")
#     is_duitable.text = 'Y'  # preguntando eso

#     currency_code = SubElement(shipment_details, "CurrencyCode")
#     currency_code.text = 'USD'

#     shipper = SubElement(root, "Shipper")
#     shipper_id = SubElement(shipper, "ShipperID")
#     shipper_id.text = settings.DHL_ACCOUNT
#     shipper_company_name = SubElement(shipper, "CompanyName")
#     shipper_company_name.text = 'MEXICAN CULTURE TRADE AND COMMERCE'
#     shipper_registered_account = SubElement(shipper, "RegisteredAccount")
#     shipper_registered_account.text = settings.DHL_ACCOUNT
#     shipper_address_line = SubElement(shipper, "AddressLine")
#     shipper_address_line.text = 'AV FUERZA AEREA MEXICANA 540'  # cambiar
#     shipper_city = SubElement(shipper, "City")
#     shipper_city.text = 'MEXICO DF'  # cambiar
#     shipper_division = SubElement(shipper, "Division")
#     shipper_division.text = 'VENUSTIANO CARRANZA'  # cambiar
#     shipper_postal_code = SubElement(shipper, "PostalCode")
#     shipper_postal_code.text = '15700'  # cambiar
#     shipper_country_code = SubElement(shipper, "CountryCode")
#     shipper_country_code.text = 'MX'
#     shipper_country_name = SubElement(shipper, "CountryName")
#     shipper_country_name.text = 'MEXICO'

#     shipper_contact = SubElement(shipper, "Contact")
#     shipper_contact_person_name = SubElement(shipper_contact, "PersonName")
#     shipper_contact_person_name.text = 'Daniel Careaga'
#     shipper_contact_person_name = SubElement(shipper_contact, "PhoneNumber")
#     shipper_contact_person_name.text = '+5215532252057'
#     shipper_contact_person_name = SubElement(shipper_contact, "Email")
#     shipper_contact_person_name.text = 'contacto@mexeart.com'

#     e_proc_ship = SubElement(root, "EProcShip")
#     e_proc_ship.text = 'N'

#     label_image = SubElement(root, "LabelImageFormat")
#     label_image.text = 'PDF'

#     archive_doc = SubElement(root, "RequestArchiveDoc")
#     archive_doc.text = 'Y'

#     number_archive_doc = SubElement(root, "NumberOfArchiveDoc")
#     number_archive_doc.text = '2'

#     r = requests.post(settings.DHL_URL, data=tostring(root))

#     response = fromstring(r.content)

#     return {
#         'tracking_number': response.find('AirwayBillNumber').text,
#         'base64_image': response.find('LabelImage').find('OutputImage').text
#     }


# @login_required
# @csrf_protect
# @require_POST
# def shipping_quotes(request, address_id):
#     to_address = get_object_or_404(Address, pk=address_id)

#     cart = get_cart(request)

#     services = []

#     shipping_methods = ShippingMethod.objects.filter(active=True)

#     for method in shipping_methods:

#         if method.name == 'DHL':

#             for dhl_service in dhl_quote(cart, to_address):
#                 services.append(dhl_service)

#         elif method.name == 'UPS':

#             for ups_service in ups_quote(cart, to_address):
#                 services.append(ups_service)

#         else:

#             services.append(
#                 {'method_id': method.pk, 'service_name': method.name, 'service_delivery_date': '',
#                  'service_cost': str(method.cost),'service_code':''})

#     return JsonResponse(json.dumps(services), safe=False)
