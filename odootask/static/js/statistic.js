		 $(function(){

String.prototype.format = function(args) {  
    var result = this;  
    if (arguments.length > 0) {      
        if (arguments.length == 1 && typeof (args) == "object") {  
            for (var key in args) {  
                if(args[key]!=undefined){  
                    var reg = new RegExp("({" + key + "})", "g");  
                    result = result.replace(reg, args[key]);  
                }  
            }  
        }  
        else {  
            for (var i = 0; i < arguments.length; i++) {  
                if (arguments[i] != undefined) {  
                    //var reg = new RegExp("({[" + i + "]})", "g");//这个在索引大于9时会有问题  
                    var reg = new RegExp("({)" + i + "(})", "g");  
                    result = result.replace(reg, arguments[i]);  
             }  
          }  
       }  
   }  
   return result;  
}  
                        var colors = [ "active", "success", "warning", "danger" ];
                        var curr_date = new Date();
                        var year = curr_date.getFullYear();
                        var month = curr_date.getMonth() + 1;
                        var day = curr_date.getDate();
                        $.get("/task_statistic",{"start_time":"{0}-{1}-{2} 00:00:00".format(year, month, day), "end_time":"{0}-{1}-{2} 23:59:59".format(year, month, day) }, function(data){
                            $("#category_tbody").html("");
                            $("#community_tbody").html("");
                            var statistic_data = data.data;
                            var categoty_statistic_data = statistic_data[0];
                            var community_statistic_data = statistic_data[1];
                            for(var i=0, len=categoty_statistic_data.length; i<len; i++){
                                $("#category_tbody").append('<tr class="{0}"><td>{1}</td><td>{2}</td></tr>'.format(colors[ i%4 ], categoty_statistic_data[i][0], categoty_statistic_data[i][1]));
}
                            for(var i=0, len=community_statistic_data.length; i<len; i++){
                                $("#community_tbody").append('<tr class="{0}"><td>{1}</td><td>{2}</td></tr>'.format(colors[ i%4 ], community_statistic_data[i][0], community_statistic_data[i][1]));
}
                        }, "json");
		});
