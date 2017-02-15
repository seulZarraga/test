from django.contrib.algoliasearch import AlgoliaIndex


class ProductIndex(AlgoliaIndex):
    fields = ('product_name',
              'public_price',
              'low_distr_price',
              'med_distr_price',
              'high_distr_price',
              'category',
              'buy_link',
              'image',
              'product_image_url')

    settings = {
        "attributesForFaceting": ['category', ],
        "attributesToIndex": ["product_name", "category", 'get_seller.nombre'],
        # "customRanking": ["desc(inscritos)", "desc(visitas)"],
        "ignorePlurals": True,
        "removeStopWords": True,
        "hitsPerPage": 8,
        "unretrievableAttributes": ["visits"]}

    should_index = 'can_index'
