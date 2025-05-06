from PIL import Image, ImageDraw
from queue import PriorityQueue

class Cavaleiro:
    def __init__(self, nome, poder):
        self.nome = nome
        self.poder = poder
        self.energia = 5

    def pode_lutar(self):
        return self.energia > 0

    def lutar(self):
        self.energia -= 1


class MapaZodiaco:
    def __init__(self, arquivo_mapa):
        self.walls = []
        self.casas = {}
        self.start = None
        self.goal = None

        with open(arquivo_mapa) as f:
            linhas = f.read().splitlines()

        self.height = len(linhas)
        self.width = max(len(l) for l in linhas)
        linhas = [linha.ljust(self.width) for linha in linhas]

        casa_id = 1
        for i in range(self.height):
            row = []
            for j in range(self.width):
                c = linhas[i][j]
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
                    self.casas[(i, j)] = casa_id
                    casa_id += 1
                    row.append("casa")
                else:
                    row.append("plano")
            self.walls.append(row)

        self.cavaleiros = [
            Cavaleiro("Seiya", 1.5),
            Cavaleiro("Shiryu", 1.4),
            Cavaleiro("Hyoga", 1.3),
            Cavaleiro("Shun", 1.2),
            Cavaleiro("Ikki", 1.1)
        ]

    def custo_terreno(self, estado):
        tipo = self.walls[estado[0]][estado[1]]
        return {"casa": 0 , "plano": 1, "rochoso": 5, "montanha": 200}.get(tipo, 1)

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

    def heuristic(self, estado, objetivo):
        distancia = abs(estado[0] - objetivo[0]) + abs(estado[1] - objetivo[1])
        terreno = self.custo_terreno(estado)
        return distancia + terreno

    def selecionar_time(self):
        vivos = [c for c in self.cavaleiros if c.pode_lutar()]
        if not vivos:
            raise Exception("Todos os cavaleiros estao mortos!")

        # Rotaciona entre os cavaleiros vivos, 2 por luta
        time = []
        for _ in range(2):
            if not vivos:
                break
            c = vivos[self.vez_do_cavaleiro % len(vivos)]
            time.append(c)
            self.vez_do_cavaleiro += 1

        return time
    
    # LUTAR
    def lutar_em_casa(self, casa_id, state):
        if state in self.casas_visitadas:
            return
        dificuldade = self.dificuldades.get(casa_id, 100)
        time = self.selecionar_time()
        poder_total = sum(c.poder for c in time)
        tempo = round(dificuldade / poder_total, 2)
        for c in time:
            c.lutar()
        nomes = ", ".join(c.nome for c in time)
        self.solucoes.append(f"Casa {casa_id}: {nomes} lutaram. Tempo: {tempo} min")
        self.tempo_total += tempo
        self.casas_visitadas.add(state)

    def verificar_casas_visitadas(self, caminho):
        Qcasas_visitadas = 0
        total_casas = len(self.casas)  # Número total de casas no mapa
        
        for i in range(len(caminho)):
            if self.walls[caminho[i][0]][caminho[i][1]] == "casa":
                Qcasas_visitadas += 1    
        
        if Qcasas_visitadas == total_casas:
            print("visitou todas")
        else:
            print("não visitou todas")
                        
    def resolve(self, inicio, objetivo):
        fronteira = PriorityQueue()
        fronteira.put((0, inicio))
        veio_de = {inicio: None}
        custo_ate_agora = {inicio: 0}
        self.explored = []  # Mudamos para lista para manter a ordem
        self.explored_set = set()  # Mudamos para lista para manter a ordem

        Casas_visitadas=0
        
        while not fronteira.empty():
            _, atual = fronteira.get()
            # lutou = 0 #todo : para debug
            if atual == objetivo:
                break
            
            # Expandir vizinhos e escolher o mais promissor(com base na heurística)
            for _, vizinho in self.neighbors(atual):
                # se achar uma casa ,lutar 
                    # verificar  se já lutou na casa
                estadoAtual = self.walls[vizinho[0]][vizinho[1]]
                if (estadoAtual == "casa" and estadoAtual not in self.explored):
                    self.lutar_em_casa(self.casas[vizinho], estadoAtual)           
                    # lutou+=1 #todo : para debug                  
                
                novo_custo = custo_ate_agora[atual] + self.custo_terreno(vizinho)
                if vizinho not in custo_ate_agora or novo_custo < custo_ate_agora[vizinho]:
                    custo_ate_agora[vizinho] = novo_custo
                    prioridade = novo_custo + self.heuristic(vizinho, objetivo)
                    fronteira.put((prioridade, vizinho))
                    veio_de[vizinho] = atual  
                    self.explored.append(vizinho)
                    self.explored_set.add(vizinho)
                    # print("andou\n") #todo : para debug                    
            
        # Reconstrói o caminho
        atual = objetivo
        caminho = []
        while atual != inicio:
            caminho.append(atual)
            atual = veio_de.get(atual)
            if atual is None:
                print("Caminho não encontrado.")
                return [], []
                    
        caminho.append(inicio)
        caminho.reverse()
        

        # VERIFICAR SE PASSOU POR TODAS AS CASAS
        self.verificar_casas_visitadas(caminho)

        self.melhor_caminho = caminho
        return caminho, list(custo_ate_agora.keys())

    def visualizar(self, caminho=None, nome_arquivo="caminho_zodiaco.png"):
        tamanho = 50
        img = Image.new("RGB", (self.width * tamanho, self.height * tamanho), "white")
        draw = ImageDraw.Draw(img)

        for i in range(self.height):
            for j in range(self.width):
                tipo = self.walls[i][j]
                cor = {"plano": "white", "rochoso": "gray", "montanha": "black"}.get(tipo, "white")
                draw.rectangle(
                    [j*tamanho, i*tamanho, (j+1)*tamanho, (i+1)*tamanho],
                    fill=cor,
                    outline="black"
                )

        if caminho:
            for (i, j) in caminho:
                draw.rectangle(
                    [j*tamanho, i*tamanho, (j+1)*tamanho, (i+1)*tamanho],
                    fill="yellow"
                )

        i, j = self.start
        draw.rectangle(
            [j*tamanho, i*tamanho, (j+1)*tamanho, (i+1)*tamanho],
            fill="blue"
        )

        i, j = self.goal
        draw.rectangle(
            [j*tamanho, i*tamanho, (j+1)*tamanho, (i+1)*tamanho],
            fill="green"
        )

        img.save(nome_arquivo)
        print(f"Imagem salva como: {nome_arquivo}")


# Execução
mapa = MapaZodiaco("mazeR.txt")
inicio = mapa.start
objetivo = mapa.goal

melhor_caminho, explorados = mapa.resolve(inicio, objetivo)

print("Início:", inicio)
print("Objetivo:", objetivo)
print("\nMelhor caminho até o objetivo:")
for pos in melhor_caminho:
    print(pos)

# Gera imagem com o melhor caminho em amarelo
mapa.visualizar(caminho=melhor_caminho)
