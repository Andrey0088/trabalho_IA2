from flask import Flask, jsonify, send_from_directory
import json
import heapq
import os
from flask import Flask, jsonify, send_from_directory, render_template
import json, heapq, os



app = Flask(__name__, static_folder='static', template_folder='templates')

app = Flask(__name__)

# Diretorio onde o arquivo 'caminho.json' será salvo
STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.g = g
        self.h = h

    def f(self):
        return self.g + self.h

    def __lt__(self, other):
        return self.f() < other.f()

class MapaZodiaco:
    def __init__(self, mapa, start, end):
        self.mapa = mapa
        self.start = start
        self.end = end

    def valida_posicao(self, pos):
        return 0 <= pos[0] < len(self.mapa) and 0 <= pos[1] < len(self.mapa[0]) and self.mapa[pos[0]][pos[1]] != 'X'

    def heuristica(self, pos):
        return abs(pos[0] - self.end[0]) + abs(pos[1] - self.end[1])

    def gerar_vizinhos(self, node):
        vizinhos = []
        movimentos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        for movimento in movimentos:
            vizinho = (node.state[0] + movimento[0], node.state[1] + movimento[1])
            if self.valida_posicao(vizinho):
                vizinhos.append(vizinho)
        return vizinhos

    def a_star(self):
        start_node = Node(state=self.start)
        open_list = []
        heapq.heappush(open_list, start_node)
        closed_list = set()
        came_from = {}

        while open_list:
            current_node = heapq.heappop(open_list)

            if current_node.state == self.end:
                path = []
                while current_node:
                    path.append(current_node.state)
                    current_node = current_node.parent
                return path[::-1]  # Caminho inverso

            closed_list.add(current_node.state)

            for neighbor in self.gerar_vizinhos(current_node):
                if neighbor in closed_list:
                    continue
                g_cost = current_node.g + 1
                h_cost = self.heuristica(neighbor)
                neighbor_node = Node(state=neighbor, parent=current_node, g=g_cost, h=h_cost)
                if neighbor_node not in open_list:
                    heapq.heappush(open_list, neighbor_node)

        return []

@app.route('/get_caminho')
def get_caminho():
    mapa = [
        ['S', '.', '.', 'X', '.', '.', '.'],
        ['.', 'X', '.', 'X', '.', '.', '.'],
        ['.', '.', '.', '.', '.', 'X', 'E']
    ]
    start = (0, 0)  # Posição de início
    end = (2, 6)    # Posição de fim

    mapa_zodiaco = MapaZodiaco(mapa, start, end)
    caminho = mapa_zodiaco.a_star()

    # Salvando o caminho em um arquivo JSON na pasta 'static'
    caminho_json = {"caminho": caminho}
    with open(os.path.join(STATIC_FOLDER, 'caminho.json'), 'w') as f:
        json.dump(caminho_json, f)

    return jsonify({"caminho": caminho})

@app.route('/static/<path:filename>')
def send_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
