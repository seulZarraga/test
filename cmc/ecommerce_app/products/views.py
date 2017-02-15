from django.shortcuts import render, render_to_response, get_object_or_404

from django.template import RequestContext

from products.models import Product

from distribuidor.models import Distribuidor


def product_page(request, product_id, slug):

    context = RequestContext(request)

    product = get_object_or_404(Product, pk=product_id)

    return render_to_response('products/product_page.html',
                              {'product': product}, context)
