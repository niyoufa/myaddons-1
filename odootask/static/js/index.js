$(function(){
    initGoodSearchPage();

    function initGoodSearchPage(){
        $("#number")[0].blur();
    }

    $("#number").focus(function(){
        $("#number")[0].blur();
        location.href = "/search.html" ;
    });

    $.get("/nearby_donate",{},function(data){
        if(data.code != 1){
            alert("加载数据失败!");
            return;
        }
        result = data.data.goods;
        for(var i=0,len=result.length;i<len;i++){
            $("#nearby_donate").append(String.format(''+
                '<div class="good-tab row">'+
                    '<div class="col-xs-4">'+
                            '<p>{0}</p>'+
                            '<p>{1}</p>'+
                    '</div>'+
                    '<div class="col-xs-8 tab-content">'+
                        '<p>'+
                            '捐赠人：{2}'+
                        '</p>'+
                        '<p>'+
                            '捐赠物资 : {3}'+
                        '</p>'+
                    '</div>'+
                '</div>'
            ,result[i].show_date,result[i].show_time,result[i].donator_id[1],result[i].category_id[1]));
        }
    },"json");

    $("div.title span").click(function(){
        $($(this).parent().parent()).find("div.good-tab-list").toggle();
    });

    $.get("/hot_good_types",{},function(data){
        if(data.code != 1){
                alert("加载数据失败!");
                return;
            }
            result = data.data.good_types;
            $("#donate_good").empty();
            for(var i=0,len=result.length;i<len;i++){
                $("#donate_good").append(String.format(''+
                    '<div class="good-tab row">'+
                       '<div class="col-xs-4">'+
                           '<img src="/image?category_id={4}" alt="暂无图片" class="float-left" />'+
                       '</div>'+
                       '<div class="col-xs-8 tab-content">'+
                           '<p>社区： {0}</p>'+
                           '<p>名称 : {1}</p>'+
                           '<p>规格 : {2}</p>'+
                           '<p>累计义捐数量 : {3} </p>'+
                       '</div>'+
                       '<span class="category_id" style="display:none;">{4}</span>'+
                    '</div>'
                ,result[i].community[1],result[i].name,result[i].unit[1],result[i].donator_amount,
                    result[i].id));
            }
            $("#donate_good div.good-tab").click(function(){
                var category_id = $(this).find("span.category_id").text();
                location.href = "/category_detail.html?category_id="+category_id;
            });
    },"json");

});