from __future__ import unicode_literals

from django.apps import AppConfig
from django.contrib import algoliasearch
from products.index import ProductIndex


class ProductsConfig(AppConfig):
    name = 'products'

    def ready(self):
        product = self.get_model('Product')
        algoliasearch.register(product, ProductIndex)
