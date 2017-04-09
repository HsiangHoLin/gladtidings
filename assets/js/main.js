var resize_background = function() {

	/* To let image-fixed become image-scroll in mobile
	 * */

	if ($(window).width() > 1024) {
		$( ".myback" ).css("background-attachment", "fixed");
	} else {
		$( ".myback" ).css("background-attachment", "scroll");
	}
}

$(document).ready(function () {

    $(".mlink").click(function(){
        var target = this.getAttribute('data-target');
        $('html, body').animate({
           scrollTop: $(target).offset().top
        }, 800, 'easeOutCubic');
    });

	$(window).resize(function() {
  		resize_background();
	});

});

