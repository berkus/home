$(document).ready(function(){
    
    $(".page").height($(document).height()/4);

    $(".page").css('margin-bottom', $(document).height()/25);

    $(".page").hover(
        function(){
            $(this).addClass("hover");
        },
        function(){
            $(this).removeClass("hover");
        }
    );

    $(".page").click(function(){
        window.location=$(this).find("a").attr("href");
        return false;
    });
});