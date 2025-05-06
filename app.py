from flask import Flask, render_template, request, jsonify
from teste import ZodiacoMapAStar  # Importe a classe ZodiacoMapAStar

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Página inicial com upload do mapa

@app.route('/resolver', methods=['POST'])
def resolver():
    if 'mapa' not in request.files:
        return "Arquivo não encontrado", 400

    mapa = request.files['mapa']
    mapa.save('mapa.txt')  # Salva o mapa enviado no servidor

    # Resolve o mapa
    zodiaco = ZodiacoMapAStar('mapa.txt')
    zodiaco.solve()
    resultado = zodiaco.solution  # Contém o caminho e as casas visitadas

    # Retorna o resultado em formato JSON
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
