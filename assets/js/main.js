$(document).ready(function () {

    $(".mlink").click(function(){
        var target = this.getAttribute('data-target');
        $('html, body').animate({
           scrollTop: $(target).offset().top
        }, 800, 'easeOutCubic');
    });

    $('.editor').trumbowyg();
});

