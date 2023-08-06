
document.getElementById("search").onclick = function() {search()};


function search() {
    var apiKey = document.getElementById("api").value;
    var source = new EventSource('/'+apiKey+'/1');
    source.onmessage = function(e) {
        console.log(e.data);
        if (e.data === "close"){
            console.log("Fechando stream");
            source.close();
        } else{
            document.getElementById("response").innerHTML=e.data;
        }
    }
}
