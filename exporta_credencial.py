import json

with open("credenciais/gdrive_credenciais.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

json_escape = json.dumps(dados)
print(json_escape)
