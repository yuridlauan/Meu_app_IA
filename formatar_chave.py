import json

# Caminho do arquivo de credenciais JSON original
caminho_json = "credenciais/gdrive_credenciais.json"

# Nome da seção no secrets (ex: [gdrive_credenciais])
nome_secrets = "gdrive_credenciais"

with open(caminho_json, "r") as f:
    dados = json.load(f)

print(f"[{nome_secrets}]")
for chave, valor in dados.items():
    # Aspas duplas para strings
    if isinstance(valor, str):
        valor = f'"{valor}"'
    print(f"{chave} = {valor}")
