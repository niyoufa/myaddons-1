$(function(){

    $("#donate_type").change(function(){
        var donate_type = $("#donate_type").val();
        if(!donate_type){
            alert("请选择义捐方式");
            return;
        }
    });
});