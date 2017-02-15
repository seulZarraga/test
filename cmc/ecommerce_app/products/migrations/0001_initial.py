# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-02-06 19:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(blank=True, max_length=200)),
                ('public_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True)),
                ('low_distr_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True)),
                ('med_distr_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True)),
                ('high_distr_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True)),
                ('description', models.TextField(blank=True, max_length=3000)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(default=True)),
                ('stock', models.IntegerField(blank=True, default=0, null=True)),
                ('sku', models.CharField(blank=True, max_length=200)),
                ('buy_link', models.CharField(blank=True, default='example.com', max_length=255)),
                ('image', models.ImageField(blank=True, default='/static/images/default_product.jpg', max_length=300, null=True, upload_to='product_image')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Category')),
            ],
        ),
    ]
