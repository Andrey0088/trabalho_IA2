import sys
from queue import PriorityQueue
from PIL import Image, ImageDraw, ImageFont
import copy
import json

class Cavaleiro:
    def __init__(self, nome, poder):
        self.nome = nome
        self.poder = poder
        self.energia = 5

    def pode_lutar(self):
        return self.energia > 0

    def lutar(self):
        self.energia -= 1

    def clone(self):
        novo = Cavaleiro(self.nome, self.poder)
        novo.energia = self.energia
        return novo

class Node:
    def __init__(self, state, parent, action, cost, heuristic, casas_visitadas, cavaleiros, tempo, batalhas):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic
        self.casas_visitadas = casas_visitadas
        self.cavaleiros = cavaleiros
        self.tempo = tempo
        self.batalhas = batalhas  # lista de dicionários com informações das batalhas

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

class ZodiacoMap:
    def __init__(self, filename):
        self.walls = []
        self.casas = {}
        self.start = None
        self.goal = None

        with open(filename) as f:
            contents = f.read().splitlines()

        self.height = len(contents)
        self.width = max(len(line) for line in contents)
        contents = [line.ljust(self.width) for line in contents]

        casa_count = 1
        for i in range(self.height):
            row = []
            for j in range(self.width):
                c = contents[i][j]
                if c == "R":
                    self.start = (i, j)
                    row.append("plano")
                elif c == "G":
                    self.goal = (i, j)
                    row.append("plano")
                elif c == "#":
                    row.append("montanha")
                elif c == ".":
                    row.append("rochoso")
                elif c == "C":
                    self.casas[(i, j)] = casa_count
                    casa_count += 1
                    row.append("casa")
                else:
                    row.append("plano")
            self.walls.append(row)

        if not self.start or not self.goal:
            raise Exception("Mapa precisa ter R e G")

        self.dificuldades = {
            1: 50, 2: 55, 3: 60, 4: 70, 5: 75, 6: 80,
            7: 85, 8: 90, 9: 95, 10: 100, 11: 110, 12: 120
        }

    def custo_terreno(self, estado):
        tipo = self.walls[estado[0]][estado[1]]
        return {"casa": 0, "plano": 1, "rochoso": 5, "montanha": 200}.get(tipo, 1)

    def neighbors(self, estado):
        linha, col = estado
        direcoes = [
            ("up", (linha - 1, col)),
            ("down", (linha + 1, col)),
            ("left", (linha, col - 1)),
            ("right", (linha, col + 1))
        ]
        return [
            (acao, (l, c)) for acao, (l, c) in direcoes
            if 0 <= l < self.height and 0 <= c < self.width
        ]

    def selecionar_time(self, cavaleiros, casa_id):
        # Ordena os cavaleiros primeiro por energia restante (priorizando os que ainda podem lutar) e depois pelo poder cósmico
        cavaleiros_disponiveis = sorted(
            [c for c in cavaleiros if c.pode_lutar()],
            key=lambda c: (c.energia, c.poder),
            reverse=True
        )

        # Seleciona até dois cavaleiros para lutar
        if len(cavaleiros_disponiveis) == 0:
            return [], float('inf')  # Nenhum cavaleiro disponível

        time_selecionado = cavaleiros_disponiveis[:2]  # Escolher até dois cavaleiros

        # Calcula a dificuldade da casa e o tempo de batalha baseado no poder combinado dos selecionados
        dificuldade = self.dificuldades.get(casa_id, 100)
        poder_total = sum(c.poder for c in time_selecionado)
        tempo_batalha = round(dificuldade / poder_total, 2)

        return time_selecionado, tempo_batalha

    def lutar_em_casa(self, casa_id, cavaleiros):
        time, tempo_batalha = self.selecionar_time(cavaleiros, casa_id)

        if not time:
            return float('inf'), cavaleiros, []  # Retorna "infinito" se nenhum cavaleiro estiver disponível

        # Atualiza a energia dos cavaleiros que participaram da batalha
        for cavaleiro in time:
            cavaleiro.lutar()

        return tempo_batalha, cavaleiros, [c.nome for c in time]


    def cavaleiros_vivos(self, cavaleiros):
        return any(c.pode_lutar() for c in cavaleiros)

    def heuristic(self, estado, casas_faltando):
        if casas_faltando:
            distancias = [abs(estado[0] - c[0]) + abs(estado[1] - c[1]) for c in casas_faltando]
            return min(distancias)
        else:
            return abs(estado[0] - self.goal[0]) + abs(estado[1] - self.goal[1])

    def solve(self):
        cavaleiros_iniciais = [
            Cavaleiro("Seiya", 1.5),
            Cavaleiro("Shiryu", 1.4),
            Cavaleiro("Hyoga", 1.3),
            Cavaleiro("Shun", 1.2),
            Cavaleiro("Ikki", 1.1)
        ]

        start_node = Node(
            state=self.start,
            parent=None,
            action=None,
            cost=0,
            heuristic=self.heuristic(self.start, set(self.casas.keys())),
            casas_visitadas=frozenset(),
            cavaleiros=cavaleiros_iniciais,
            tempo=0,
            batalhas=[]
        )

        frontier = PriorityQueue()
        frontier.put((start_node.cost + start_node.heuristic, start_node))
        explored = set()

        while not frontier.empty():
            _, node = frontier.get()

            state = node.state
            casas = set(node.casas_visitadas)
            cav_energias = tuple(c.energia for c in node.cavaleiros)
            chave_explorada = (state, cav_energias, frozenset(casas))
            if chave_explorada in explored:
                continue
            explored.add(chave_explorada)

            if state in self.casas and state not in casas:
                tempo_luta, novos_cavaleiros, lutadores = self.lutar_em_casa(self.casas[state], copy.deepcopy(node.cavaleiros))
                if tempo_luta == float('inf'):
                    continue
                casas.add(state)
                cavaleiros = novos_cavaleiros
                tempo_total = node.tempo + tempo_luta
                batalhas = node.batalhas + [{
                    "posicao": state,
                    "tempo": tempo_luta,
                    "cavaleiros": lutadores
                }]
            else:
                cavaleiros = copy.deepcopy(node.cavaleiros)
                tempo_total = node.tempo
                batalhas = node.batalhas.copy()

            if state == self.goal and len(casas) == len(self.casas) and self.cavaleiros_vivos(cavaleiros):
                caminho, atual = [], node
                while atual.parent:
                    caminho.append(atual.state)
                    atual = atual.parent
                caminho.reverse()

                self.solution = caminho
                self.explored = [e[0] for e in explored]

                dados_json = {
                    "caminho": caminho,
                    "batalhas": batalhas,
                    "cavaleiros_escolhidos": [c.nome for c in cavaleiros if c.pode_lutar()]
                }

                with open("saida_caminho_zodiaco.json", "w", encoding="utf-8") as f:
                    json.dump(dados_json, f, indent=4, ensure_ascii=False)

                print(f"Caminho encontrado: {len(caminho)} passos")
                print(f"Tempo total: {tempo_total} minutos")
                return

            for action, neighbor in self.neighbors(state):
                custo = node.cost + self.custo_terreno(neighbor)
                h = self.heuristic(neighbor, set(self.casas.keys()) - casas)
                novo_node = Node(
                    state=neighbor,
                    parent=node,
                    action=action,
                    cost=custo,
                    heuristic=h,
                    casas_visitadas=frozenset(casas),
                    cavaleiros=cavaleiros,
                    tempo=tempo_total,
                    batalhas=batalhas
                )
                frontier.put((novo_node.cost + novo_node.heuristic, novo_node))

    def visualizar(self, nome_arquivo):
        cell = 30
        borda = 1
        img = Image.new("RGB", (self.width * cell, self.height * cell), "black")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        solucao = set(self.solution) if hasattr(self, 'solution') else set()

        for i in range(self.height):
            for j in range(self.width):
                x0, y0 = j * cell + borda, i * cell + borda
                x1, y1 = (j + 1) * cell - borda, (i + 1) * cell - borda

                pos = (i, j)
                tipo = self.walls[i][j]
                if pos == self.start:
                    fill = (255, 0, 0)
                elif pos == self.goal:
                    fill = (0, 255, 0)
                elif pos in solucao:
                    fill = (255, 255, 0)
                elif pos in self.casas:
                    fill = (0, 0, 255)
                elif tipo == "montanha":
                    fill = (105, 105, 105)
                elif tipo == "rochoso":
                    fill = (169, 169, 169)
                elif tipo == "plano":
                    fill = (255, 255, 255)
                else:
                    fill = (40, 40, 40)

                draw.rectangle([x0, y0, x1, y1], fill=fill)

        img.save(nome_arquivo)
        print(f"Imagem salva como {nome_arquivo}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Uso: python zodiaco_solver_a_star.py mapa.txt")

    z = ZodiacoMap(sys.argv[1])
    print("Resolvendo com A*...")
    z.solve()
    z.visualizar("saida_zodiaco.png")

