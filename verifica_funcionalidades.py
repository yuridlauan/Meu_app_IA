import os
import pandas as pd
from funcoes_compartilhadas import conversa_banco

# Caminho da pasta onde estão as páginas
PASTA_PAGINAS = "paginas"

# Lê a tabela de funcionalidades do Google Sheets
df = conversa_banco.select("funcionalidades", {
    "ID": "id",
    "ID_Menu": "texto",
    "Nome": "texto",
    "Caminho": "texto"
})

# Lista de arquivos reais da pasta
arquivos_existentes = [f.replace(".py", "") for f in os.listdir(PASTA_PAGINAS) if f.endswith(".py")]

# Valida se os arquivos existem
df["Arquivo Existe?"] = df["Caminho"].apply(lambda nome: nome in arquivos_existentes)

# Filtra os que estão com erro
faltando = df[df["Arquivo Existe?"] == False]

if faltando.empty:
    print("\n✅ Todos os caminhos das funcionalidades estão corretos.")
else:
    print("\n⚠️ Arquivos ausentes na pasta 'paginas':\n")
    for _, row in faltando.iterrows():
        print(f"❌ {row['Nome']} → Caminho: {row['Caminho']}.py")
