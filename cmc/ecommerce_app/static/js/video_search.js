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
    if (dataLayer[0].pageType.indexOf("Videos Search Page") > -1) {
        var search = instantsearch({
            appId: ALGOLIA_APPLICATION_ID,
            apiKey: ALGOLIA_SEARCH_KEY,
            indexName: ALGOLIA_INDEX,
            urlSync: true
        });


        search.addWidget(
            instantsearch.widgets.searchBox({
                container: '#id_q'
            })
        );

        search.addWidget(
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


        search.addWidget(
            instantsearch.widgets.refinementList({
                container: '#genero',
                attributeName: 'genero',
                operator: 'or',
                templates: {
                    item: function (data) {
                        checked = ""

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

        search.addWidget(
            instantsearch.widgets.refinementList({
                container: '#director',
                attributeName: 'get_director',
                operator: 'or',
                sortBy: ['name:asc'],
                templates: {
                    item: function (data) {
                        checked = ""

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

        search.addWidget(
            instantsearch.widgets.refinementList({
                container: '#tipo',
                attributeName: 'tipo',
                operator: 'or',
                templates: {
                    item: function (data) {
                        checked = ""

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

        var noResultsTemplate = '<h4 class="text-center" style="margin-top: 40px;">We are sorry, we couldn\'t find any video that matches <i>\'{{query}}\'</i></h4>';


        search.addWidget(
            instantsearch.widgets.hits({
                container: '#hits',
                hitsPerPage: 9,
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

                        iterate(data)

                        
                        var video_template =
                            '<div class="col-xs-12 col-sm-4 col-md-4" style="margin-bottom:20px;">' +
                            '<div class="col-item">' +
                            '<div class="photo">' +
                            '<a href="'+data.video_page_url+'"><img src="'+data.video_image_url+'" class="img-responsive" alt="video thumbnail"/></a>' +
                            '</div>' +
                            '<div class="info text-center">' +
                            '<div class="row">' +
                            '<div class="price">' +
                            '<h5>'+data.title+'</h5>' +
                            '<h4>'+data.get_director+'</h4>' +
                            '<p>' + data.tipo + ' | ' + data.genero + ' | ' + data.duracion + '</p>' +
                            '</div>' +
                            '</div>' +
                            '<div class="separator clear-left">' +
                            '<p class="btn-add">' +
                            '<a href="'+data.profile_url+'" class="btn btn-primary">Artist Profile</a></p>' +
                            '</div>' +
                            '<div class="clearfix">' +
                            '</div>' +
                            '</div>' +
                            '</div>' +
                            '</div>'

                        return video_template

                    }
                }
            })
        );


        search.addWidget(
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


        search.start()


        var onRenderHandler2 = function() {

            pages = parseInt(search.helper.lastResults.nbPages)

            if(pages > 1){

                $('.pagination').show()

            } else{
                $('.pagination').hide()
            }

        };

        search.on('render', onRenderHandler2);



        onRenderHandler = function() {

            var product_template =
                            '<div class="col-xs-12 col-sm-4 col-md-4" style="margin-bottom:20px;">' +
                            '<div class="col-item">' +
                            '<div class="photo">' +
                            '<img src="' + MORE_SOON + '" class="img-responsive" alt="product image"/></a>' +
                            '</div>' +
                            '<div class="info text-center">' +
                            '<div class="row">' +
                            '<div class="price">' +
                            '<h5>More Products Coming Soon</h5>' +
                            '</div>' +
                            '</div>' +
                            '</div>' +
                            '</div>' +
                            '</div>'


            $('.ais-hits').append(product_template)

        };

        search.once('render', onRenderHandler);

    } //end if algolia


});