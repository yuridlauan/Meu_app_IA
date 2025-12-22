# formatar_chave.py

import json

# Caminho do arquivo dentro da pasta 'credenciais'
input_path = "credenciais/gdrive_credenciais.json"

with open(input_path, "r") as f:
    data = json.load(f)

# Substitui quebras de linha da private_key por '\\n'
data["private_key"] = data["private_key"].replace("\n", "\\n")

# Imprime em formato compatível com Streamlit secrets.toml
print("[gdrive_credenciais]")
for k, v in data.items():
    print(f'{k} = "{v}"')
