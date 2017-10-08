$(function(){
    $("#loading").hide();
    initGoodSearchPage();

    function initGoodSearchPage(){
        if($("#list_number").length){
            $("#list_number")[0].focus();
        }
    }

    $("#cancel_search").click(function(){
        $("#more_category_list").empty();
        get_more_category(1,10);
    });

    $("#list_number").blur(function(){
        var phone = $("#list_number").val();
        $("#loading").show();
        $.get("/goods",{"phone":phone},function(data){
            $("#loading").hide();
            if(data.code != 1){
                alert("加载数据失败!");
                return;
            }
            result = data.data.goods;
            $("#good_search_list").empty();
            for(var i=0,len=result.length;i<len;i++){
                $("#good_search_list").append(String.format(''+
                    '<div class="good-tab row">'+
                        '<div class="col-xs-4">'+
                                '<img src="/image?category_id={6}" alt="" class="float-left"/>'+
                        '</div>'+
                        '<div class="col-xs-8 tab-content">'+
                            '<p>'+
                                '捐赠人：{1}'+
                            '</p>'+
                            '<p>'+
                                '捐赠物资 : {2}'+
                            '</p>'+
                            '<p>'+
                                '捐赠社区 : {5}'+
                            '</p>'+
                            '<p>'+
                                '日期 {3}'+
                            '</p>'+
                        '</div>'+
                        '<span class="good_numer" style="display:none;">{4}<span>'+
                    '</div>'
                ,result[i].number,result[i].donator_id[1],result[i].category_id[1],result[i].create_date,result[i].number,
                result[i].community[1], result[i].category_id[0]));
            }
            $(".good-tab").click(function(){
                var good_number = $(this).find(".good_numer").text();
                location.href = "/detail.html?number="+good_number;
            });
        },"json");
        
    });


    var pager = null ;
    var flag = true;

    // 更多最近捐赠
    if($("#more_donate_list").length){
        get_more_nearby_donate(1,10);
    }

    function get_more_nearby_donate(page,page_size){
        $("#loading").show();
        $.get("/nearby_donate",{"more":true,"page_size":page_size,"page":page},function(data){
        $("#loading").hide();
        if(data.code != 1){
            alert("加载数据失败!");
            return;
        }
        result = data.data.goods;
        for(var i=0,len=result.length;i<len;i++){
            $("#more_donate_list").append(String.format(''+
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
        console.log(pager);
        pager = data.pager;
        flag = true;
    },"json");
    }

    // 更多最近捐赠
    // 上拉加载 下拉刷新
    if($("#more_donate_list").length){
        $(window).scroll(function() {
            //$(document).scrollTop() 获取垂直滚动的距离
            //$(document).scrollLeft() 这是获取水平滚动条的距离

            // 下拉
//            if ($(document).scrollTop() <= 0 && flag) {
//                flag = false;
//                $("#more_donate_list").empty();
//                get_more_nearby_donate(1,10);
//            }

            // 上拉
            if ($(document).scrollTop() >= $(document).height() - $(window).height() && flag) {
                flag = false;
                if(pager && pager["has_more"]){
                    page = pager['page']+1;
                    page_size = pager['page_size'];
                    get_more_nearby_donate(page,page_size);
                }else{
                    flag = true;
                }

            }
        });
    }

    // 更多义捐商品
    if($("#more_category_list").length){
        get_more_category(1,10);
    }

    function get_more_category(page,page_size){
        $("#loading").show();
        var community_name = $("#community_name").val();
        $.get("/more_good_types",{"more":true,"page_size":page_size,"page":page,
            "community_name":community_name},function(data){

            $("#loading").hide();
            if(data.code != 1){
                alert("加载数据失败!");
                return;
            }
            result = data.data.good_types;
            for(var i=0,len=result.length;i<len;i++){
                $("#more_category_list").append(String.format(''+
                    '<div class="good-tab row">'+
                       '<div class="col-xs-4">'+
                           '<img src="image?category_id={4}" alt="暂无图片" class="float-left" />'+
                       '</div>'+
                       '<div class="col-xs-8 tab-content">'+
                           '<p>社区： {0}</p>'+
                           '<p>名称 : {1}</p>'+
                           '<p>规格 : {2}</p>'+
                           '<p>单价 : {5}</p>'+
                           '<p>累计义捐数量 : {3} </p>'+
                       '</div>'+
                       '<span class="category_id" style="display:none;">{4}</span>'+
                    '</div>'
                ,result[i].community[1],result[i].name,result[i].unit[1],result[i].donator_amount,
                    result[i].id, result[i].price));
            }
            $("#more_category_list div.good-tab").click(function(){
                var category_id = $(this).find("span.category_id").text();
                location.href = "/category_detail.html?category_id="+category_id;
            });
            console.log(pager);
            pager = data.pager;
            flag = true;
        },"json");
    }

    // 更多义捐商品
    // 上拉加载 下拉刷新
    if($("#more_category_list").length){
        $(window).scroll(function() {
            //$(document).scrollTop() 获取垂直滚动的距离
            //$(document).scrollLeft() 这是获取水平滚动条的距离

            // 下拉
//            if ($(document).scrollTop() <= 0 && flag) {
//                flag = false;
//                $("#more_category_list").empty();
//                $("#community_name").val("");
//                get_more_category(1,10);
//            }

            // 上拉
            if ($(document).scrollTop() >= $(document).height() - $(window).height() && flag) {
                flag = false;
                if(pager && pager["has_more"]){
                    page = pager['page']+1;
                    page_size = pager['page_size'];
                    get_more_category(page,page_size);
                }else{
                    flag = true;
                }

            }
        });


        // 根据社区名称匹配
        //$("#community_name").blur(function(){
        //    flag = false;
        //    $("#more_category_list").empty();
        //    get_more_category(1,10);
        //});
       
        $("#do_search").click(function(){
 	    $("#more_category_list").empty();
            get_more_category(1,10);
        });

    }

});
