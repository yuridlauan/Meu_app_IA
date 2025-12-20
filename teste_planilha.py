from funcoes_compartilhadas.conversa_banco import select

TIPOS_TESTE = {
    "ID": "id"
}

df = select("Porangatu", TIPOS_TESTE)
print(df)
