## dfimoveis (Versão 0.16rc)
Webscrapping do site DFImóveis

### 1. Pré-requisitos (Windows x64)
#### - Python 3.12 [Download](https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe)
#### - Git 2.44 [Download](https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe)
##### - Se você tem versões anteriores a estas não se preocupe, é bem capaz de funcionar

### 2. Instalando o python, clonando o repositório e deixando tudo pronto
#### - 2.1 Instale o Python e o Git com as opções recomendadas pelo instalador (adicione python ao PATH quando for pedido)
#### - 2.2 Inicie o prompt de comando (CMD) e navegue até a pasta desejada
#### - 2.3 Dentro da pasta rode ```git clone https://github.com/arthurpdesimone/dfimoveis.git``` e depois ```cd dfmimoveis```
#### - 2.4 Execute o comando ```python -m venv venv``` e na sequencia ```.\venv\Scripts\activate``` para isolar seu ambiente de desenvolvimento.

### 3. Instalando as bibliotecas e rodando
#### - 3.1 Para instalar as bibliotecas rode ```pip install flask googlemaps bs4 requests```
#### - 3.2 Dentro da pasta execute ```python main.py```
#### - 3.3 Abra seu navegador de preferência e acesse ```http://127.0.0.1:5000``` e siga as demais instruções para obter sua chave de API.
