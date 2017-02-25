import base64
import hashlib
import hmac
import logging
import json
import datetime
from django.conf import settings
from products.models import Product
# from django.db.models import Count

# from auction.models import Auction
# from core.models import MapActiveStates
# from orders.models import OrderHasProducts
# from products.models import Product


def algolia(request):
    algolia_app_id = getattr(settings, 'ALGOLIA', False)['APPLICATION_ID']

    algolia_search_key = getattr(settings, 'ALGOLIA', False)['SEARCH_KEY']

    algolia_index = getattr(settings, 'ALGOLIA', False)['INDEX_PREFIX']

    response = {'ALGOLIA_INDEX': algolia_index}

    if algolia_app_id:
        response['ALGOLIA_APPLICATION_ID'] = algolia_app_id

    if algolia_search_key:
        response['ALGOLIA_SEARCH_KEY'] = algolia_search_key

    return response


def conekta(request):
    response = {}

    conekta_public_key = getattr(settings, 'CONEKTA_PUBLIC_KEY', False)

    if conekta_public_key:
        response['CONEKTA_PUBLIC_KEY'] = conekta_public_key

    return response


def map_active_states(request):

    states = {}

    # active_states = MapActiveStates.objects.filter(is_active=True)

    # for state in active_states:
    #     states[str(state.estado)] = 100

    # return {'MAP_ACTIVE_STATES': base64.b64encode(json.dumps(states))}
    return {'states': states}


def index_catalog(request):

    herbomex = Product.objects.filter(category__name='HERBOMEX').order_by('?')[:4]
    girarcamps = Product.objects.filter(category__name='GIRARCAMPS').order_by('?')[:4]

    print herbomex

    return {'herbomex': herbomex,
            'girarcamps': girarcamps}


def top_products_nav(request):
    date_limit = datetime.datetime.now() - datetime.timedelta(days=14)

#     # Top Folk art products

#     folk_art_orders = OrderHasProducts.objects.filter(product__category1__name="Folk Art").filter(
#         order__date_created__gte=date_limit).values('product').annotate(
#         Count('product')).order_by('-product')[:3]

#     top_folk_prods = []

#     if not folk_art_orders.exists():

#         top_folk_prods = Product.objects.filter(category1__name="Folk Art").order_by('?')[:3]

#     else:

#         for folk in folk_art_orders:
#             top_folk_prods.append(Product.objects.get(pk=folk['product']))

#     # Top Mexican Artist products

#     mexican_artists_orders = OrderHasProducts.objects.filter(product__category1__name='Mexican Artists').filter(
#         order__date_created__gte=date_limit).values('product').annotate(Count('product')).order_by('-product')[:3]

#     top_mexican_artits = []

#     if not mexican_artists_orders.exists():

#         mexican_artists_orders = Product.objects.filter(category1__name='Mexican Artists').order_by('?')[:3]

#     else:

#         for mexican in mexican_artists_orders:
#             top_mexican_artits.append(Product.objects.get(pk=mexican['product']))

#     mexeart_design_orders = OrderHasProducts.objects.filter(product__mexeart_design=True).filter(
#         order__date_created__gte=date_limit).values('product').annotate(Count('product')).order_by('-product')[:3]

#     top_mexeart_design = []

#     if not mexeart_design_orders.exists():
#         mexeart_design_orders = Product.objects.filter(mexeart_design=True)

#     else:

#         for mexeart in mexeart_design_orders:
#             top_mexeart_design.append(Product.objects.get(pk=mexeart['product']))

#     # Top auction

#     top_auction_prods = []

#     top_auction = Auction.objects.filter(due_timestamp__gte=datetime.datetime.now()).order_by('due_timestamp')[:3]

#     if not top_auction.exists():

#         top_auction_prods = Product.objects.filter(sell_type='auction').order_by('?')[:3]

#     else:

#         for auction in top_auction:
#             top_auction_prods.append(auction.product)

#     return {'TOP_FOLK_ART': top_folk_prods, 'TOP_MEXEART': top_mexeart_design,
#             'TOP_MEXICAN_ARTISTS': top_mexican_artits, 'TOP_AUCTION': top_auction_prods}
    return {'status': '202'}
