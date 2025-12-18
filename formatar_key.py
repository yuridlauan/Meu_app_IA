# formatar_key.py

def formatar_chave_para_toml(caminho_arquivo):
    with open(caminho_arquivo, 'r') as file:
        chave = file.read().strip()

    chave_toml = chave.replace('\n', '\\n')
    print('\nCopie e cole no secrets.toml:')
    print(f'private_key = """{chave_toml}"""')

# Caminho para o seu key.txt (salvo no mesmo diretório)
formatar_chave_para_toml("key.txt")
