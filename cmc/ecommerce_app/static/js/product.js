/**
 * Created by Agustino on 14/07/16.
 */

$(function () {

    /* wait for images to load */
    $(window).load(function () {

        $("#img_01").elevateZoom({
            responsive: true,
            gallery: 'gal1',
        });




    });

    $('#read-more-desc').click(function(event){

        event.preventDefault();
        $('#product-desc-short').hide();
        $('#product-desc-long').show();
        $('#read-about-artist').hide();
        $('#read-less-desc').show();
        $(this).hide()

    });

    $('#read-less-desc').click(function(event){

        event.preventDefault();
        $('#product-desc-short').show();
        $('#product-desc-long').hide();
        $('#read-more-desc').show();
        $(this).hide()

    });

    $('#read-more-artist').click(function(event){

        event.preventDefault();
        $('#read-about-artist').show();
        $('#product-desc-long').hide();
        $('#product-desc-short').show();
        $('#read-less-artist').show();
        $(this).hide()

    });

    $('#read-less-artist').click(function(event){

        event.preventDefault();
        $('#read-about-artist').hide();
        $('#product-desc-long').hide();
        $('#product-desc-short').show();
        $('#read-more-artist').show();
        $(this).hide()

    });

    $("#background_img").change(function() {

        input = this;

        if (input.files && input.files[0]) {
                var reader = new FileReader();

                var image = new Image();

                var height = 0

                reader.onload = function (e) {

                    image.src = e.target.result;

                    image.onload = function() {
                        // access image size here
                        height = this.height;
                    }

                    $('#background_img_div')
                        .css('background','url("'+e.target.result+'") no-repeat center center fixed')
                        .css('-webkit-background-size','contain')
                        .css('-moz-background-size','contain')
                        .css('-o-background-size','contain')
                        .css('background-size','contain')
                        .css('width','100%')
                        .css('height','1000px')
                };


                $('#upload_pic_step2').show()

                reader.readAsDataURL(input.files[0]);
            }

    });

    function dragMoveListener (event) {
    var target = event.target,
        // keep the dragged position in the data-x/data-y attributes
        x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
        y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

    // translate the element
    target.style.webkitTransform =
    target.style.transform =
      'translate(' + x + 'px, ' + y + 'px)';

    // update the posiion attributes
    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
  }

  // this is used later in the resizing and gesture demos
  window.dragMoveListener = dragMoveListener;

    interact('.resize-drag')
      .draggable({
        onmove: window.dragMoveListener,
        restrict: {
          restriction: 'parent'
        }
      })
      .resizable({
        preserveAspectRatio: true,
        edges: { left: true, right: true, bottom: true, top: true }
      })
      .on('resizemove', function (event) {
        var target = event.target,
            x = (parseFloat(target.getAttribute('data-x')) || 0),
            y = (parseFloat(target.getAttribute('data-y')) || 0);

        // update the element's style
        target.style.width  = event.rect.width + 'px';
        target.style.height = event.rect.height + 'px';

        // translate when resizing from top or left edges
        x += event.deltaRect.left;
        y += event.deltaRect.top;

        target.style.webkitTransform = target.style.transform =
            'translate(' + x + 'px,' + y + 'px)';

        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);
        target.textContent = Math.round(event.rect.width) + '×' + Math.round(event.rect.height);
      });


});