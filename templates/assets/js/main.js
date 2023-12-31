var baixando = false;
var source;

document.getElementById("search").onclick = function() {
    search();
    document.getElementById("search-icon").style.display="none";
    document.getElementById("spinner").style.display="block";
};

//Modal instruções
var locModal = document.getElementById('modal-instrucoes');
var btnclose = document.getElementById('prosseguir');
btnclose.addEventListener('click', (e) => {
    locModal.style.display = "none";
    locModal.className="modal fade";
});


function search() {
 
    var apiKey = document.getElementById("api").value;
    var pagina = document.getElementById("pagina-final").value;
    var endereco = document.getElementById("endereco").value;
    var quartos = document.getElementById("quartos").value;
    var vagas = document.getElementById("vagas").value;
    console.log("Parâmetros de pesquisa: página:"+pagina+" endereço:"+endereco+" quartos:"+quartos+" vagas:"+vagas);
    console.log(baixando);
    if(baixando===true){
        source.close();
        source = new EventSource('/'+apiKey+'/'+pagina+'/'+endereco+'/'+quartos+'/'+vagas);
    }else{
        source = new EventSource('/'+apiKey+'/'+pagina+'/'+endereco+'/'+quartos+'/'+vagas);
    }
    var registros = pagina*30;

    //Limpa a tabela
    document.querySelectorAll("table tbody tr").forEach(function(e){e.remove()})
    //Reinicializa progress bar
    var bar = document.querySelector(".progress-bar");
    bar.style.width = 0 + "%";
    bar.innerText = 0 + "%";

    source.onmessage = function(e) {
        console.log(e.data);
        if (e.data === "close"){
            console.log("Fechando stream");
            document.getElementById("search-icon").style.display="block";
            document.getElementById("spinner").style.display="none";
            source.close();
            baixando = false;
        } else{
            baixando = true;
            const dados = JSON.parse(e.data);
            //Pegando ordem
            var ordem = dados.ordem;
            //Pegando índice
            var indice = dados.indice;
            //Pegando endereço
            var endereco = dados.endereco;
            //Pegando cidade
            var cidade = dados.cidade;
            //Pegando tipo
            var tipo = dados.tipo;
            //Pegando preço
            var preco = dados.preco;
            //Pegando área
            var area = dados.area;
            //Pegando distância de carro
            var carro = dados.duracao_carro;
            //Pegando distância de transporte público
            var transporte = dados.duracao_transp_pub;
            //Pegando link
            var link = dados.link;
            //Pegando e-mail
            var email = dados.email;
            //Pegando whatsapp
            var whatsapp = dados.whatsapp;
            //Populando a tabela
            var tabela = document.getElementById("dataTable").getElementsByTagName('tbody')[0];
            var linha = tabela.insertRow();
            var indice_celula = linha.insertCell(0);
            indice_celula.innerHTML = indice;
            var endereco_celula = linha.insertCell(1);
            endereco_celula.innerHTML = endereco;
            var cidade_celula = linha.insertCell(2);
            cidade_celula.innerHTML = cidade;
            var tipo_celula = linha.insertCell(3);
            tipo_celula.innerHTML = tipo;
            var preco_celula = linha.insertCell(4);
            preco_celula.innerHTML = preco;
            var area_celula = linha.insertCell(5);
            area_celula.innerHTML = area;
            var carro_celula = linha.insertCell(6);
            carro_celula.innerHTML = carro;
            var transporte_celula = linha.insertCell(7);
            transporte_celula.innerHTML = transporte;
            var link_celula = linha.insertCell(8);
            link_celula.innerHTML = "<a href='"+link+"' target='blank'><i class='fa fa-link' style='font-size:24px;color:green'></i></a>";
            var email_celula = linha.insertCell(9);
            email_celula.innerHTML = email;
            var whatsapp_celula = linha.insertCell(10);
            if(whatsapp.includes("whatsapp")){
                whatsapp_celula.innerHTML = "<a href='"+whatsapp+"' target='blank'><i class='fa fa-whatsapp' style='font-size:24px;color:green'></i></a>";
            }else{
                whatsapp_celula.innerHTML = whatsapp;
            }
            
            //Preenche progress bar
            var pcg = Math.floor(ordem/registros*100);
            console.log(pcg);
            //document.getElementById("progress-bar-animated").setAttribute('aria-valuenow',pcg);
            var bar = document.querySelector(".progress-bar");
            bar.style.width = pcg + "%";
            bar.innerText = pcg + "%";
        }
    }
}

function sortTable(table, col, reverse) {
    var tb = table.tBodies[0], // use `<tbody>` to ignore `<thead>` and `<tfoot>` rows
        tr = Array.prototype.slice.call(tb.rows, 0), // put rows into array
        i;
    reverse = -((+reverse) || -1);
    tr = tr.sort(function (a, b) { // sort rows
        return reverse // `-1 *` if want opposite order
            * (a.cells[col].textContent.trim() // using `.textContent.trim()` for test
                .localeCompare(b.cells[col].textContent.trim(), undefined, {numeric: true})
               );
    });
    for(i = 0; i < tr.length; ++i) tb.appendChild(tr[i]); // append each row in order
}

function makeSortable(table) {
    var th = table.tHead, i;
    th && (th = th.rows[0]) && (th = th.cells);
    if (th) i = th.length;
    else return; // if no `<thead>` then do nothing
    while (--i >= 0) (function (i) {
        var dir = 1;
        th[i].addEventListener('click', function () {sortTable(table, i, (dir = 1 - dir))});
    }(i));
}

function makeAllSortable(parent) {
    parent = parent || document.body;
    var t = parent.getElementsByTagName('table'), i = t.length;
    while (--i >= 0) makeSortable(t[i]);
}

window.onload = function () {
    makeAllSortable();
    document.getElementById("spinner").style.display="none";

    //Reinicia a progress bar
    var bar = document.querySelector(".progress-bar");
    bar.style.width = 0 + "%";
    bar.innerText = 0 + "%";

    document.querySelector(".modal").classList.add("show");
    document.querySelector(".modal").style.display = "block";
};

$(document).ready(function () {
    $(".tablesorter").tablesorter();
    $("#dataTable").stickyTableHeaders();
  });

  var width = $(window).width();
  var height = $(window).height();
  if (width < 1000 || height < 500) {
      alert("Você necessita de um dispositivo com resolução melhor");
  }