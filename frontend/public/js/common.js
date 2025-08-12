$(function() {
    scroll();
});

function scroll(){
    $(window).scroll(function(){
        if($(this).scrollTop() > 100){
            $('.navbar-default').addClass('active');
        }else{
            $('.navbar-default').removeClass('active');
        }
    });
}

