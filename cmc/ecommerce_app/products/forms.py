# -*- coding: utf-8 -*-
from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name',
                  'public_price',
                  'low_distr_price',
                  'med_distr_price',
                  'high_distr_price',
                  'description',
                  'category',
                  'sku',
                  'buy_link',
                  'image',
                  )
