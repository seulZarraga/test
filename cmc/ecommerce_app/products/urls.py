"""Projects URL'S."""
from django.conf.urls import patterns, url

# place app url patterns here

from products import views


urlpatterns = patterns(
    '',
    url(r'^$', 'core.views.search', name='search_products'),
    url(r'^(?P<user_id>[0-9]+)/$', 'core.views.search', name='search_products_user'),
    url(r'^producto/(?P<product_id>[0-9]+)/(?P<slug>[\w-]+)/$', views.product_page, name='product_page'),
)