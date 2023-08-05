
'''
@author: Arthur Pendragon De Simone
'''
from datetime import datetime
import googlemaps as googlemaps
from flask import Flask, render_template

app = Flask(__name__, static_folder='templates/assets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<api>',methods=['GET'])
def download_imoveis(api_key):
    gmaps = googlemaps.Client(key=api_key)
    carro_direcoes = gmaps.directions("Rua Dias De Oliveira, 192",
                                      "Rua Vespasiano, 76",
                                      mode="driving",
                                      avoid="ferries",
                                      departure_time= datetime.now()
                                      )
    return carro_direcoes[0]

if __name__ == "__main__":
 app.run()