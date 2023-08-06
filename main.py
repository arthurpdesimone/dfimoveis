
'''
@author: Arthur Pendragon De Simone
'''
import json
import time
import traceback
from datetime import datetime
import googlemaps as googlemaps
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, session, flash, Response, stream_with_context

app = Flask(__name__, static_folder='templates/assets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test/<api>')
def test(api):
    gmaps = googlemaps.Client(key=api)
    now = datetime.now()
    carro_direcoes = gmaps.directions('Rua Dias de Oliveira, 192',
                                      'Rua Vespasiano, 76',
                                      mode="driving",
                                      avoid="ferries",
                                      departure_time=now
                                      )
    return json.dumps(carro_direcoes)

@app.route('/<api>/<pagina>',methods=['GET'])
def download_imoveis(api,pagina):
    def event_stream():
        while True:
            yield "data:" + "test" + "\n\n"
            time.sleep(1)
    def gerar_resposta(api,pagina):
        lista_imoveis = []
        endereco_a_comparar = 'Banco do Brasil Sede III - Brasilia'
        gmaps = googlemaps.Client(key=api)
        # Fonte DF Imóveis

        link = f'http://www.dfimoveis.com.br/aluguel/df/todos/imoveis/1,2-quartos?vagasdegaragem=1&ordenamento=menor-valor&pagina={pagina}'
        requisicao = requests.get(link)

        soup = BeautifulSoup(requisicao.text, "html.parser")
        imoveis = soup.find_all('a', class_='new-card')
        # Loop pelos imóveis
        for imovel in imoveis:
            try:
                # Scrapping
                link = imovel['href']
                link_base = 'http://www.dfimoveis.com.br'
                link_request = link_base + link
                imovel_request = requests.get(link_request)
                imovel_soup = BeautifulSoup(imovel_request.text, "html.parser")

                # Dados relevantes
                endereco = imovel_soup.find('h1', class_='mb-0 font-weight-600 fs-1-5')
                preco = imovel_soup.find('small', class_='display-5 text-warning precoAntigoSalao')
                area = imovel_soup.find('small', class_='display-5 text-warning')
                area = float(area.text.replace(' ', '').replace('m²', '').replace(',', '.'))
                cidade = imovel_soup.find_all('h6', class_='mb-0 text-normal text-nowrap')[1].find('small',
                                                                                                   class_='text-muted').text
                email_anunciante = ''

                latitude = imovel_soup.find_all('script')
                lat = 0
                lon = 0
                for l in latitude:
                    if 'latitude' in l.text:
                        array_coordenadas = l.text.replace("\r\n", '').replace(' ', '').split(';')
                        lat = array_coordenadas[1].split('=')[1]
                        lon = array_coordenadas[2].split('=')[1]

                try:
                    email_anunciante = imovel_soup.find('input', {'id': 'emailDoAnunciante'}).get('value')
                except Exception as e:
                    print(e)

                condominio = 0
                try:
                    condominio = imovel_soup.find('div', class_='col-12 col-sm-5').find('small',
                                                                                        class_='text-muted').text
                except Exception as e:
                    condominio = 0

                preco = int(preco.text.replace('.', '')) + int(condominio)
                now = datetime.now()

                # Direções
                endereco_completo = endereco.text + ' ' + cidade
                transp_pub_direcoes = gmaps.directions(str(lat) + ',' + str(lon),
                                                       endereco_a_comparar,
                                                       mode="transit",
                                                       avoid="ferries",
                                                       departure_time=now
                                                       )
                carro_direcoes = gmaps.directions(str(lat) + ',' + str(lon),
                                                  endereco_a_comparar,
                                                  mode="driving",
                                                  avoid="ferries",
                                                  departure_time=now
                                                  )
                # Resultados da API do GMaps
                duracao_transp_pub = transp_pub_direcoes[0]['legs'][0]['duration']['text']
                duracao_carro = carro_direcoes[0]['legs'][0]['duration']['text']

                # Tratamento dos resultados
                duracao_transp_pub = duracao_transp_pub.replace('hour', ',').replace('mins', '').replace('min',
                                                                                                         '').replace(
                    ' ', '')
                duracao_carro = duracao_carro.replace('hour', ',').replace('mins', '').replace('min', '').replace(' ',
                                                                                                                  '')
                array_carro = duracao_carro.split(',')
                array_transp_pub = duracao_transp_pub.split(',')

                # Se tem minutos, o array é divido em dois valores, um com os minutos e outro com as horas
                if len(array_carro) > 1:
                    duracao_carro = int(array_carro[0]) * 60 + int(array_carro[1])
                else:
                    duracao_carro = int(array_carro[0])

                if len(array_transp_pub) > 1:
                    duracao_transp_pub = int(array_transp_pub[0]) * 60 + int(array_transp_pub[1])
                else:
                    duracao_transp_pub = int(array_transp_pub[0])

                # Calcula o índice
                indice = preco * ((duracao_transp_pub + duracao_carro) ** 2) / area

                # Imprime o resultado
                print(
                    f'Indice: {indice:.1f} \t Endereço: {endereco.text + cidade} \t Preço: R$ {preco} \t Área: {area} m2 \t ETA carro: {duracao_carro} min \t ETA transp. pub: {duracao_transp_pub} min \t Link: {link_request}')

                # Salva o dicionario
                imovel_dict = {'indice': indice,
                               'endereco': endereco.text + cidade,
                               'preco': preco,
                               'area': area,
                               'duracao_carro': duracao_carro,
                               'duracao_transp_pub': duracao_transp_pub,
                               'link': link_request,
                               'email': email_anunciante}
                lista_imoveis.append(imovel_dict)
                yield "data:"+str(json.dumps(lista_imoveis))+"\n\n"
            except Exception as e:
                traceback.print_exc()
        yield "data:close\n\n"
    response = Response(stream_with_context(gerar_resposta(api, pagina)), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    return response
if __name__ == "__main__":
    app.secret_key = 'secret key'
    app.run()
