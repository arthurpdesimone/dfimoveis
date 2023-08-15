
'''
@author: Arthur Pendragon De Simone
'''
import json
import sys
import traceback
import urllib
from datetime import datetime
import googlemaps as googlemaps
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, session, flash, Response, stream_with_context

app = Flask(__name__, static_folder='templates/assets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<api>/<pagina>/<endereco_a_comparar>/<quartos>/<vagas>',methods=['GET'])
def download_imoveis(api,pagina,endereco_a_comparar,quartos,vagas):
    def gerar_resposta(api,pagina,endereco_a_comparar,quartos,vagas):
        print(pagina)
        print(endereco_a_comparar)
        print(quartos)
        print(vagas)
        ordem = 1
        endereco_a_comparar = str(endereco_a_comparar) + '- Brasilia'
        gmaps = googlemaps.Client(key=api)
        print(f"API KEY {api}", file=sys.stderr)
        for p in range(1,int(pagina)+1):
            # Fonte DF Imóveis
            link = f'https://www.dfimoveis.com.br/aluguel/df/todos/imoveis?quartosinicial={quartos}&quartosfinal={quartos}&vagasdegarageminicial={vagas}&vagasdegaragemfinal={vagas}&ordenamento=menor-valor&pagina={p}'
            requisicao = requests.get(link)
            print(link)
            soup = BeautifulSoup(requisicao.text, "html.parser")
            imoveis = soup.find_all('a', class_='new-card')
            # Loop pelos imóveis
            for imovel in imoveis:
                try:
                    # Scrapping
                    link = imovel['href']
                    link_base = 'https://www.dfimoveis.com.br'
                    link_request = link_base + link
                    imovel_request = requests.get(link_request)
                    imovel_soup = BeautifulSoup(imovel_request.text, "html.parser")

                    # Dados relevantes
                    endereco = imovel_soup.find('h1', class_='mb-0 font-weight-600 fs-1-5')
                    preco = imovel_soup.find('small', class_='display-5 text-warning precoAntigoSalao')
                    area = imovel_soup.find('small', class_='display-5 text-warning')
                    tipo = imovel_soup.findAll('h6',class_='text-normal mb-0')[2].text.replace('Aluguel de ','').strip()
                    tipo = tipo.replace('Padrão','').replace('Kitnet-Studio','')
                    area = round(float(area.text.replace(' ', '').replace('m²', '').replace(',', '.')))
                    cidade = imovel_soup.find_all('h6', class_='mb-0 text-normal text-nowrap')[1].find('small',class_='text-muted').text
                    # Whatsapp ou telefone
                    link_whatsapp = imovel_soup.find('a',class_='abrirModalWhatsapp')
                    try:
                        link_whatsapp = link_whatsapp['data-link']
                        idx1 = link_whatsapp.index("https://")
                        idx2 = link_whatsapp.index("&text=")
                        link_whatsapp = link_whatsapp[idx1: idx2]+"&text="+link_request
                    except Exception as e:
                        telefone = imovel_soup.find('a',class_='abrirTelefone')
                        telefone = telefone['href'].replace('tel:','')
                        link_whatsapp=telefone

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

                    condominio = "0"
                    try:
                        condominio = imovel_soup.find('div', class_='col-12 col-sm-5').find('small',
                                                                                            class_='text-muted').text
                    except Exception as e:
                        condominio = "0"

                    preco = int(preco.text.replace('.', '')) + int(condominio.replace('.',''))

                    # Direções
                    endereco_completo = endereco.text + ' ' + cidade
                    transp_pub_direcoes,carro_direcoes = localiza_google_maps(gmaps,endereco_completo,endereco_a_comparar,lat,lon)

                    # Resultados da API do GMaps
                    duracao_transp_pub = transp_pub_direcoes[0]['legs'][0]['duration']['text']
                    duracao_carro = carro_direcoes[0]['legs'][0]['duration']['text']
                    # Tratamento dos resultados
                    duracao_transp_pub = duracao_transp_pub.replace('hours',',').replace('hour', ',').replace('mins', '').replace('min','').replace(' ', '')

                    duracao_carro = duracao_carro.replace('hours',',').replace('hour', ',').replace('mins', '').replace('min', '').replace(' ','')

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
                    if area > 0:
                        indice = round(preco * ((duracao_transp_pub + duracao_carro) ** 2) / area)
                    else:
                        indice = 0

                    # Imprime o resultado
                    print(
                        f'Indice: {indice:.1f} \t Endereço: {endereco.text + cidade} \t Preço: R$ {preco} \t Área: {area} m2 \t ETA carro: {duracao_carro} min \t ETA transp. pub: {duracao_transp_pub} min \t Link: {link_request}')

                    # Salva o dicionario
                    imovel_dict = {'ordem': ordem,
                                   'indice': indice,
                                   'endereco': endereco.text,
                                   'cidade': cidade,
                                   'tipo':tipo,
                                   'preco': 'R$ '+str(preco),
                                   'area': str(area)+' m²',
                                   'duracao_carro': str(duracao_carro)+' min',
                                   'duracao_transp_pub': str(duracao_transp_pub) +' min',
                                   'link': link_request,
                                   'email': email_anunciante,
                                   'whatsapp':link_whatsapp}
                    yield "data:"+str(json.dumps(imovel_dict))+"\n\n"
                except Exception as e:
                    print("Fechando stream", file=sys.stderr)
                    print(e, file=sys.stderr)
                    traceback.print_exc()
                ordem+=1
        yield "data:close\n\n"
    response = Response(stream_with_context(gerar_resposta(api,pagina,endereco_a_comparar,quartos,vagas)), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    return response


def localiza_google_maps(gmaps,endereco_completo,endereco_a_comparar,lat,lon):
    now = datetime.now()
    transp_pub_direcoes = ""
    carro_direcoes = ""
    try:
        transp_pub_direcoes = gmaps.directions(endereco_completo,
                                               endereco_a_comparar,
                                               mode="transit",
                                               avoid="ferries",
                                               departure_time=now
                                               )
        carro_direcoes = gmaps.directions(endereco_completo,
                                          endereco_a_comparar,
                                          mode="driving",
                                          avoid="ferries",
                                          departure_time=now
                                          )
    except Exception as e:
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

    if not transp_pub_direcoes or not carro_direcoes:
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

    return transp_pub_direcoes,carro_direcoes

if __name__ == "__main__":
    app.secret_key = 'secret key'
    app.run()
