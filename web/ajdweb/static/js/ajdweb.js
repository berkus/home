$(document).ready(function(){
    
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

