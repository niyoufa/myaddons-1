$(function(){

var api_path = "http://139.224.26.81:8500";
//      var api_path = "http://localhost:8500";

    var category_id = location.href.split("?category_id=")[1];
    $.get("/good_type",{"category_id":category_id},function(data){
        if(data.code != 1){
            alert("加载数据失败!");
            return;
        }
        result = data.data.good_type;
        if(result){
            console.log(result);
            $("#category_image").attr("src","/image?category_id="+String(result.id))
            $("#name").html(result.name);
            $("#good_type").html(result.id);
            $("#unit").html(result.unit[1]);
            $("#community").html(result.community[1]);
            $("#community_id").html(result.community[0]);
            $("#donator_amount").html(String(result.donator_amount) + "份");
            $("#donatee_amount").html(String(result.donatee_amount) + "份");
            $("#source").html(result.source);
            $("#price").html("￥" + result.price);
        }
    },"json");

    $("#go_to_donate").click(function(){
        $("#good_detail").hide();
        $("#pay_page").show();
        clearDonateInfo();
    });

    $("#get_phone_code").click(function(){
        $("#get_phone_code").css({"color":"#337ab7"});
        var phone = $("#phone").val();
        if(phone==""){
            alert("请输入手机号!");
            return;
        }
        $.get(api_path + "/api/checkcode/mobile",{"mobile":phone},function(data){
            $("#get_phone_code").attr("disabled",true);
            if(data.response.success != 1){
                alert(data.response.return_code);
                $("#get_phone_code").attr("disabled",false);
                return;
            }
            var index = 60;
            var interval_obj = setInterval(function(){
                    index = index -1;
                    $("#get_phone_code").html(String(index) + "s") ;
                    if(index == 1){
                        index = 60;
                        $("#get_phone_code").html("获取验证码") ;
                        $("#get_phone_code").attr("disabled",false);
                        clearInterval(interval_obj);
                    }
            },1000);
            console.log(data.response.data.code);

            $.get("/donator",{"mobile":phone},function(data){
                if(data.code != 1){
                    return;
                }
                var donator = data.data.donator;
                var donator_name = donator.donator_name;
                var cardid = donator.cardid;
                $("#donator_name").val(donator_name);
                $("#cardid").val(cardid);
                return;
            },"json") ;

        },"json");
    });

    function clearDonateInfo(){
        $("#phone").val("");
        $("#phone_code").val("");
        $("#donator_name").val("");
        $("#donator_count").val("");
        $("#donator_count").val("");
        $("#remark").val("");
    }

    $("#go_to_pay").click(function(){
        var community_id = $("#community_id").text();
        var phone = $("#phone").val();
        var phone_code = $("#phone_code").val();
        var donator_name = $("#donator_name").val();
        var good_type = $("#good_type").text();
        var amount = $("#donator_count").val();
        var remark = $("#remark").val();

        if(amount == ""){
            alert("请输入数量!");
            return;
        }else if(isNaN(Number(amount))){
            alert("数量格式错误!");
            $("#donator_count").val("");
            return;
        }
        if(community_id==""){
            alert("请选择捐赠社区!");
            return;
        }
        if(phone==""){
            alert("请输入手机号!");
            return;
        }else if(phone != "" && phone_code == ""){
            alert("请输入手机验证码!");
            return;
        }
        else if(donator_name==""){
            alert("请输入姓名");
            return;
        }
        else if(!good_type){
            alert("请选择捐赠物品类型!");
            return;
        }

        //验证手机验证码
        $.post(api_path + "/api/mobile/check",{"phone":phone,"phone_code":phone_code},function(data){
            if(data.response.success != 1){
                alert("验证码错误!");
                return;
            }

            var good = {
                "community_id":community_id,
                "phone":phone,
                "donator_name":donator_name,
                "good_type":good_type,
                "amount":amount,
                "remark":remark,
            }
            $.post("/upload",good,function(data){
                if(data.code != 1){
                    alert("提交异常!");
                    return;
                }
                console.log(data.data);
                alert("义捐成功,稍后您将收到短信通知！");
                location.href = "/index.html";
            },"json");

        },"json");
    });

    $("#back_to_good_detail").click(function(){
        $("#pay_page").hide();
        $("#good_detail").show();
    });
})