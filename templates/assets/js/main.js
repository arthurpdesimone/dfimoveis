
document.getElementById("search").onclick = function() {
    search();
    document.getElementById("search-icon").style.display="none";
    document.getElementById("spinner").style.display="block";
};


function search() {
    var apiKey = document.getElementById("api").value;
    var source = new EventSource('/'+apiKey+'/1');
    source.onmessage = function(e) {
        console.log(e.data);
        if (e.data === "close"){
            console.log("Fechando stream");
            document.getElementById("search-icon").style.display="block";
            document.getElementById("spinner").style.display="none";
            source.close();
        } else{
            const dados = JSON.parse(e.data);
            //Pegando índice
            var indice = dados.indice;
            //Pegando endereço
            var endereco = dados.endereco;
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
            //Populando a tabela
            var tabela = document.getElementById("dataTable").getElementsByTagName('tbody')[0];
            var linha = tabela.insertRow();
            var indice_celula = linha.insertCell(0);
            indice_celula.innerHTML = indice;
            var endereco_celula = linha.insertCell(1);
            endereco_celula.innerHTML = endereco;
            var preco_celula = linha.insertCell(2);
            preco_celula.innerHTML = preco;
            var area_celula = linha.insertCell(3);
            area_celula.innerHTML = area;
            var carro_celula = linha.insertCell(4);
            carro_celula.innerHTML = carro;
            var transporte_celula = linha.insertCell(5);
            transporte_celula.innerHTML = transporte;
            var link_celula = linha.insertCell(6);
            link_celula.innerHTML = link;
            var email_celula = linha.insertCell(7);
            email_celula.innerHTML = email;
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
};