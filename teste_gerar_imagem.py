from pillow import Image
import numpy as np
import matplotlib.pyplot as plt

# 1. Abrir a imagem
imagem = Image.open("eda8b7ab-8499-4a88-961d-0a1d31897a52.png")
pixels = np.array(imagem)

# 2. Definir o tamanho da célula (assumindo uma grade uniforme)
cell_size = 10  # ajuste se necessário
rows = pixels.shape[0] // cell_size
cols = pixels.shape[1] // cell_size

# 3. Função para classificar a célula
def identify_cell(cell_pixels):
    avg_color = np.mean(cell_pixels.reshape(-1, 3), axis=0)
    r, g, b = avg_color

    # Verde (meta)
    if r < 100 and g > 200 and b < 100:
        return "G"
    # Vermelho (início)
    elif r > 200 and g < 100 and b < 100:
        return "R"
    # Casa (preto escuro central)
    elif np.min(cell_pixels[4:6, 4:6]) < 50:
        return "C"
    # Rochoso (claro)
    elif np.mean(avg_color) > 180:
        return "."
    # Montanha (escuro)
    else:
        return "#"

# 4. Gerar mapa corrigido
mapa_corrigido = []
for i in range(rows):
    linha = []
    for j in range(cols):
        bloco = pixels[i*cell_size:(i+1)*cell_size, j*cell_size:(j+1)*cell_size]
        tipo = identify_cell(bloco)
        linha.append(tipo)
    mapa_corrigido.append(linha)

# 5. Gerar string do mapa com bordas
def gerar_mapa_formatado(mapa):
    texto = []
    borda = "#" * (len(mapa[0]) + 2)
    texto.append(borda)
    for linha in mapa:
        texto.append("#" + "".join(linha) + "#")
    texto.append(borda)
    return "\n".join(texto)

# 6. Mostrar mapa
print(gerar_mapa_formatado(mapa_corrigido))
