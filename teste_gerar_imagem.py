
# Redefinir a função de geração de mapa formatado
def gerar_mapa_formatado(mapa):
    texto = []
    borda = "#" * (len(mapa[0]) + 2)
    texto.append(borda)
    for linha in mapa:
        texto.append("#" + "".join(linha) + "#")
    texto.append(borda)
    return "\n".join(texto)

# Gerar e exibir o mapa formatado
mapa_formatado = gerar_mapa_formatado(mapa_corrigido)
print(mapa_formatado)
