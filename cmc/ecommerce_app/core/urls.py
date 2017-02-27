"""ecommerce_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

import core.views

urlpatterns = [
    url(r'^$', core.views.home, name='home'),
    url(r'^bob/', admin.site.urls),
    url(r'^send_contact_mail/$', core.views.send_contact_email, name='send_contact_email'),
    url(r'^batch_upload/$', core.views.batch_upload, name='batch_upload'),
    url(r'^volver_admin/$', core.views.volver_admin, name='volver_admin'),
    url(r'^products_admin/$', core.views.display_products, name='display_products'),
    url(r'^add_product/$', core.views.add_product, name='add_product'),
    url(r'^edit_product/(?P<product_id>[0-9]+)/$', core.views.edit_product, name='edit_product'),
    url(r'^products/', include('products.urls', namespace='products')),
    url(r'^users/', include('distribuidor.urls', namespace='distribuidor')),
    url(r'^login/$', core.views.user_login, name='login'),
    url(r'^logout/$', core.views.user_logout, name='logout'),
    url(r'^register/$', core.views.register, name='register'),
    url(r'^user/check', 'core.views.check_user', name='check_user'),
    url(r'^user/password/reset/$', core.views.password_reset,
        {'post_reset_redirect': '/user/password/reset/done/'}, name="password_reset"),
    url(r'^user/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        core.views.password_reset_confirm,
        {'post_reset_redirect': '/user/password/done/'}),
    url(r'^user/password/done/$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^confirm/(?P<activation_key>\w+)/', core.views.confirm, name='confirm'),
    url(r'^reconfirm/(?P<activation_key>\w+)/', core.views.reconfirm, name='reconfirm'),

    #url(r'^paypal/', include('paypal.standard.ipn.urls')),
]

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
