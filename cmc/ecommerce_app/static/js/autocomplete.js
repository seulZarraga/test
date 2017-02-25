//=============== init autocomplete =============================
          var client = algoliasearch(ALGOLIA_APPLICATION_ID, ALGOLIA_SEARCH_KEY);
          var idx = client.initIndex(ALGOLIA_INDEX);
          
          function searchCallback(err, content) {
              if (content.hits.length == 0) {
                $('.queries').hide();
                return;
              }
              res = '';
              for (var i = 0; i < content.hits.length; ++i) {
                res += '<a href="'+content.hits[i].product_url+'"><table id="cart" class="table table-hover table-condensed" cellpadding="10">'
                res += '<thead>'
                res += '<tr>'
                res += '<th style="width:100%"></th>'
                res += '</tr>'
                res += '</thead>'
                res += '<tbody>'
                res += '<tr>'
                res += '<td data-th="Product">'
                res += '<div class="row">'
                res += '<div class="col-sm-4 col-xs-4"><img src="' + content.hits[i].product_image_url + '" alt="" class="img-responsive"/></div>'
                res += '<div class="col-sm-6 col-xs-6">'
                res += '<h4 class="nomargin title-alone">' + content.hits[i]._highlightResult.product_name.value +'</h4>'
                res += '</div>'
                res += '</div>'
                res += '</td>'
                res += '</tr>'
                res += '</tbody>'
                res += '</table></a>'
              }
              $('.queries').html(res);
              $('.queries').show();
          }


          function search(query) {
            if (query.length === 0) {
              $('.queries').hide();
              return;
            }

            idx.search(query, {
              hitsPerPage: 3,
              getRankingInfo: 1
            }, searchCallback);
          }

          
          $(document).ready(function() {
            var inputfield_small = $('#search_small');
            var inputfield = $('#id_q');

            inputfield_small.keyup(function() {
                search(inputfield_small.val());
            });

            inputfield.keyup(function() {
                search(inputfield.val());
            });
          });


        //=============== end autocomplete =========================//
