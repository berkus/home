$(document).ready(function(){
    $(".page").each(function(){
        $(this).hover(
            function() { $(this).addClass("hover"); },
            function() { $(this).removeClass("hover"); }
        );
        $(this).click(function(){
            window.location=$(this).find("a").attr("href");
            return false;
        });
    });
});