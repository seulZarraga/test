from __future__ import unicode_literals

from django.db import models
import os
from django.conf import settings
from slugify import slugify

# Create your models here.


class Product(models.Model):
    product_name = models.CharField(blank=True, max_length=200)
    public_price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, default=0.00)
    low_distr_price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, default=0.00)
    med_distr_price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, default=0.00)
    high_distr_price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, max_length=3000)
    category = models.ForeignKey('Category', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    stock = models.IntegerField(blank=True, null=True, default=0)
    sku = models.CharField(blank=True, max_length=200, default="")
    buy_link = models.CharField(max_length=255, blank=True, default="example.com")
    image = models.ImageField(max_length=300, upload_to='product_image',
                              default=os.path.join(settings.STATIC_URL, 'images', 'default_product.jpg'),
                              blank=True,
                              null=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, default='nombre_producto')

    @property
    def create_slug(self):
        slug = slugify(self.product_name)
        if self.slug != slug:
            self.slug = slug
        return super(Product, self).save()

    def can_index(self):
        can_index = self.available is True
        return can_index

    @property
    def product_image_url(self):

        # Pseudocode:
        if self.image == os.path.join(settings.STATIC_URL, 'images', 'default_product.jpg'):

            return self.image

        else:

            return self.image.url

    # def __unicode__(self):
    #     return str(self.product_name)


class Category(models.Model):
    """docstring for Category"""
    name = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return str(self.name)
