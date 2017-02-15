/**
 * Created by Agustino on 23/08/16.
 */

$(function () {

    // Get Cities per country on Checkout
    $('#country').change(function() {

        var country_id = $(this).val();

        $('#state').empty();

        $.ajax({
            url : "//"+location.host+"/locallity/"+country_id+"/", // the endpoint
            type : "POST", // http method
            data : {csrfmiddlewaretoken:window.CSRF_TOKEN}, // data sent with the post request

            // handle a successful response
            success : function(response) {

                var cities = response

                for (i = 0; i < cities.length; i++) {
                    $('#state').append('<option value="'+cities[i].id+'" >'+cities[i].nombre+'</option>')

                }

            },

            // handle a non-successful response
            error : function() {

                alert("Error loading cities, please contact support.")

            }

        });
    });


});