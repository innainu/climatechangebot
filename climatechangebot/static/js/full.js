
// Center the .main-div according to window resize
$(window).resize(function(){

    $('.main-div').css({
        'margin-left': (0 - $('.main-div').outerWidth())/2,
        'margin-top': (0 - $('.main').outerHeight())/2
    });

});

// // To initially run the function:
$(window).resize();