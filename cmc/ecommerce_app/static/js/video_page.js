/**
 * Created by Agustino on 14/07/16.
 */

$(function () {


    url_embed(video_url)

    function url_embed(url){
        var pattern1 = /(?:http?s?:\/\/)?(?:www\.)?(?:vimeo\.com)\/?(.+)/g;
        var pattern2 = /(?:http?s?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(.+)/g;

        var dest_div = $('#video_player')

        if(pattern1.test(url)){
            var replacement = '<iframe style="width: 100%" height="640" src="//player.vimeo.com/video/$1" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>';

            var html = url.replace(pattern1, replacement);

            dest_div.html(html)
        }


        if(pattern2.test(url)){
            var replacement = '<iframe style="width: 100%" height="640" src="//www.youtube.com/embed/$1" frameborder="0" allowfullscreen></iframe>';

            var html = url.replace(pattern2, replacement);

            dest_div.html(html)
        }

    }



});