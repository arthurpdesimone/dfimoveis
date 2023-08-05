
'''
@author: Arthur Pendragon De Simone
'''
from flask import Flask, render_template

app = Flask(__name__, static_folder='templates/assets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<api>',methods=['GET'])
def download_imoveis(api):
    return f"Hello from flask{api}"

if __name__ == "__main__":
 app.run()