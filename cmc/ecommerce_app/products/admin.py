from django.contrib import admin

from products.models import Product, Category

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name',
                    'public_price',
                    'low_distr_price',
                    'med_distr_price',
                    'high_distr_price',
                    'category',
                    )
    search_fields = ['product_name', ]

    list_filter = ('category', )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
