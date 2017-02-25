
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


def index_catalog(request):

    herbomex = Product.objects.filter(category__name='HERBOMEX').order_by('?')[:4]
    girarcamps = Product.objects.filter(category__name='GIRARCAMPS').order_by('?')[:4]

    return {'herbomex': herbomex,
            'girarcamps': girarcamps}
