/**
 * Created by Agustino on 14/07/16.
 */

$(function () {

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;")
            .replace(/\//g, "&#x2F;")
            .replace('<', 'asdsdd')
    }

    // ALGOLIA
    if (dataLayer[0].pageType.indexOf("Catalog Page") > -1) {
        var searching = instantsearch({
            appId: ALGOLIA_APPLICATION_ID,
            apiKey: ALGOLIA_SEARCH_KEY,
            indexName: ALGOLIA_INDEX ,
            urlSync: true
        });

        searching.addWidget(
            instantsearch.widgets.searchBox({
                container: '#id_q'
            })
        );

        searching.addWidget(
            instantsearch.widgets.pagination({
                container: '.pagination',
                scrollTo: '#hits',
                showFirstLast: false,
                maxPages: 100,
                padding: 5,
                labels: {
                    next: '<span class="glyphicon glyphicon-chevron-right"></span>',
                    previous: '<span class="glyphicon glyphicon-chevron-left"></span>'
                },
                cssClasses: {
                    active: 'active',
                    previous: 'previous',
                    next: 'next',
                    root: 'pagination'
                }
            })
        );

        searching.addWidget(
            instantsearch.widgets.hierarchicalMenu({
                container: '#category',
                attributes: ['category'],
                sortBy: ['name:asc'],
                templates: {
                    item: function (data) {

                        checked = ""

                        //return '<a href="" style="margin-left: 20px;font-weight: bold">' + data.name + '</a>'

                        if (data.isRefined)
                            checked = "checked"

                        return '<label style="margin-left: 35px;" class="checkbox filter-checkbox"><input type="checkbox" value="' + data.name + '" data-toggle="checkbox" ' + checked + '> ' + data.name + '</label>'
                    }
                },
                cssClasses: {
                    body: 'filterCheckbox'
                }
            })
        );

        var noResultsTemplate = '<h4 class="text-center" style="margin-top: 40px;">We are sorry, we couldn\'t find any product that matches <i>\'{{query}}\'</i></h4>';


        searching.addWidget(
            instantsearch.widgets.hits({
                container: '#hits',
                hitsPerPage: 12,
                templates: {
                    empty: noResultsTemplate,
                    item: function (data) {
                        function iterate(data) {
                            $.each(data, function (key, value) {
                                if (typeof value == 'object') {
                                    iterate(value)
                                } else {
                                    if (typeof data[key] == 'string') {
                                        data[key] = escapeHtml(data[key]);
                                    }
                                }
                            })
                            return data;
                        };

                        var price = ''

                        if(dataLayer[1].distrType.indexOf("distribuidor_bajo") > -1) {

                            price = data.low_distr_price

                        }else if(dataLayer[1].distrType.indexOf("distribuidor_medio") > -1) {

                            price = data.med_distr_price

                        }else if(dataLayer[1].distrType.indexOf("distribuidor_alto") > -1) {

                            price = data.high_distr_price

                            console.log(price)

                        }else{

                            price = data.public_price
                        }

                        iterate(data)

                        var badge = ""

                        if(parseInt(data.stock) == 0){
                            badge = '<img style="position: absolute;top: 5px;right: 10px;height: 80px;width: 80px;" src="' + OOO_BADGE + '">'
                            disabled = 'disabled'
                        }
                        
                        var product_template =
                            '<div class="col-xs-12 col-sm-4 col-md-4" style="margin-bottom:20px;">' +
                            '<div class="col-item">' +
                            '<div class="photo">' +
                            '<a href="'+data.product_url+'"><img src="'+data.product_image_url+'" class="img-responsive" alt="product image" onmouseover="this.src=\'' + data.product_image_url + '\';" onmouseout="this.src=\'' + data.product_image_url + '\';" />' + badge + '</a>' +
                            '</div>' +
                            '<div class="info text-center">' +
                            '<div class="row">' +
                            '<div class="price">' +
                            '<h5>'+data.product_name+'</h5>' +
                            '<h4>$'+price+'</h4>' +
                            '</div>' +
                            '</div>' +
                            '<div class="separator clear-left">' +
                            '<p class="btn-add">' +
                            '<a href="" class="btn btn-primary"><i class="fa fa-shopping-cart"></i> Add to Cart</a></p>' +
                            '</div>' +
                            '<div class="clearfix">' +
                            '</div>' +
                            '</div>' +
                            '</div>' +
                            '</div>'

                        return product_template

                    }
                }
            })
        );


        searching.addWidget(
          instantsearch.widgets.clearAll({
            container: '#clear-all',
            templates: {
              link: '<i class="fa fa-eraser"></i> Clear all filters'
            },
            cssClasses: {
              root: 'btn btn-block btn-default'
            },
            autoHideContainer: true
          })
        );


        searching.start()


        var onRenderHandler2 = function() {

            pages = parseInt(searching.helper.lastResults.nbPages)

            if(pages > 1){

                $('.pagination').show()

            } else{
                $('.pagination').hide()
            }

        };

        searching.on('render', onRenderHandler2);



        onRenderHandler = function() {


        };

        searching.once('render', onRenderHandler);

    } //end if algolia


});