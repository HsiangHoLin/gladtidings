
var resize_background = function() {

	/* To let jumbotron height be 100% screen height
	 * But when screen height becomes too small, fix jumbotron height */

	if ($(window).height() > 500) {
		$( ".custom-jumbo-back" ).removeClass( "fixed-height" );
		$( ".custom-jumbo-back" ).addClass( "full-height" );
	}
	else {
		$( ".custom-jumbo-back" ).removeClass( "full-height" );
		$( ".custom-jumbo-back" ).addClass( "fixed-height" );
	}

	/* To let image-fixed become image-scroll in mobile
	 * */

	if ($(window).width() > 1024) {
		$( ".custom-jumbo-back" ).css("background-attachment", "fixed");
		$( ".custom-quote-back" ).css("background-attachment", "fixed");
	} else {
		$( ".custom-jumbo-back" ).css("background-attachment", "scroll");
		$( ".custom-quote-back" ).css("background-attachment", "scroll");
	}
}

var handle_search = function() {
	var str = $('.navbar-form').children("div").children("input").val();
    var trimmed = str.split(" ").join("");
    if (trimmed.length > 0) {
		var res = str.split(" ").join("+");
      	var url = 'https://www.google.com#q=' + res + '+site:practicalevangelism.net'
        window.open(url,'_newtab');
    }
}


var main = function() {

	resize_background();

	$( window ).resize(function() {
  		resize_background();
	});

	$('#search-btn').mousedown(function(event) {
      	if(event.which == 1) { // left click
      		handle_search();
      	}
	})

	$(document).keypress(function(e) {
    	if(e.which == 13) {
        	handle_search();
    	}
	});
}

$(document).ready(main);
