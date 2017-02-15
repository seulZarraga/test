from django.conf.urls import patterns, url
from distribuidor import views

urlpatterns = patterns('',
                       url(r'^$', views.home, name='users_index'),
                       url(r'^distribuidor/(?P<user_id>[0-9]+)/$', views.distribuidor_profile, name='distr_profile'),
                       url(r'^distribuidor/(?P<user_id>[0-9]+)/editar_perfil/$', views.edit_profile, name='edit_profile'),
                       url(r'^distribuidor/(?P<user_id>[0-9]+)/descargar_catalogo/$', views.download_prices, name='download_prices'),
                       # url(r'^client/(?P<user_id>[0-9]+)/edit/$', views.client_edit, name='client_edit'),
                       # url(r'^client/(?P<user_id>[0-9]+)/(?P<address_id>[0-9]+)/$', views.remove_address, name='remove_address'),
                       # url(r'^client/(?P<user_id>[0-9]+)/(?P<address_id>[0-9]+)/edit/$', views.edit_address, name='edit_address'),
                       # url(r'^client/(?P<user_id>[0-9]+)/newshippingadd/(?P<op>[0-9]+)/$', views.new_shipping_address, name='new_shipping_address'),
                       # url(r'^seller/(?P<user_id>[0-9]+)/$', views.seller_profile, name='seller_profile'),
                       # url(r'^seller/(?P<user_id>[0-9]+)/actualiza/$', views.seller_edit, name='seller_edit'),
                       )