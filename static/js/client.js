function fillRsr(data) {
    console.log('fill rsr');
    $("#rsr").empty();
    for (var i=0; i<data.length; i++) {
        $("#rsr").append("<li><p class='result-label'>"+data[i].fname+" "+data[i].lname+"</p><p class='result-classification'>"+data[i].science+", "+data[i].field+", "+data[i].subfield+"</p></li>");
    }
}

function fillPrj(data) {
    console.log('fill prj');
    $("#prj").empty();
    for (var i=0; i<data.length; i++) {
        $("#prj").append("<li><p class='result-label'>"+data[i].name+"</p><p class='result-classification'>"+data[i].startdate+","+data[i].enddate+", "+data[i].mstid+"</p></li></ul>")
    }
}

function fillLec(data) {
    console.log('fill lec');
    var br = 0;
    for (var i=0; i<data.length; i++) {
        if (parseInt(data[i].recorded.split('-')[0])>2013) {
            $("#lec").append("<div class='col-lg-4 col-sm-6'><a href='#' class='portfolio-box'><img src='http://videolectures.net/"+data[i].url+"/screenshot.jpg' class='img-responsive' alt=''><div class='portfolio-box-caption'><div class='portfolio-box-caption-content'><div class='project-category text-faded'>"+data[i].desc.substring(0,50)+"...</div><div class='project-name'>"+data[i].title+"</div></div></div></a></div>");
            br += 1;
            if (br == 8) {
                i = data.length;
            }
        }
    }
}

function drawRsrPrjColl(data) {
    console.log('draw graph');
    drawGraph1(data);
}


$("#basic-addon2").click(function(){
    $.get("http://95.87.154.208:8888/api/all/"+$("#text").val(), function(data, status){
        fillRsr(data.rsr);
        fillPrj(data.prj);
        fillLec(data.lec);
        drawRsrPrjColl(data.graph);
    }, "json");
});
