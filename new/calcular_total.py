# Dados das casas e dificuldades
casas = [
    ("Casa de Áries", 50),
    ("Casa de Touro", 55),
    ("Casa de Gêmeos", 60),
    ("Casa de Câncer", 70),
    ("Casa de Leão", 75),
    ("Casa de Virgem", 80),
    ("Casa de Libra", 85),
    ("Casa de Escorpião", 90),
    ("Casa de Sagitário", 95),
    ("Casa de Capricórnio", 100),
    ("Casa de Aquário", 110),
    ("Casa de Peixes", 120)
]

class Cavaleiro:
    def __init__(self, nome, poder, energia):
        self.nome = nome
        self.poder = poder
        self.energia = energia

# Lista de cavaleiros
cavaleiros = [
    Cavaleiro("Seiya", 1.5, 5),
    Cavaleiro("Shiryu", 1.4, 5),
    Cavaleiro("Hyoga", 1.3, 5),
    Cavaleiro("Shun", 1.2, 5),
    Cavaleiro("Ikki", 1.1, 5)
]

def calcula(equipe, casa):
    total = 0
    for lutador in equipe:
        total += lutador.poder
    return total
        
poder_equipes = []


# Função para calcular o tempo
def calcular_tempo(casa, equipe):
    total_poder_cosmico2 = calcula(casa, equipe)
    
    total_tempo = 0
    
    # Calculando o tempo de cada casa
    i=0
    for casa, dificuldade in casas:
        total_forca = total_poder_cosmico[i]
        tempo_casa = dificuldade / total_poder_cosmico[i]
        total_tempo += tempo_casa  # Cada cavaleiro participa de 5 lutas
        i+=1
    return total_tempo

# Calcular o tempo total
tempo_total = calcular_tempo(casas, cavaleiros)

# Exibir o tempo total
print(f'O tempo total gasto na luta é: {tempo_total:.2f} unidades de tempo')

#teste 1: melhor equipe possivel pra casa de maior dificuldade