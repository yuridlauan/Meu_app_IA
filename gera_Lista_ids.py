# gera_lista_ids.py

import pandas as pd
from funcoes_compartilhadas.cria_id import cria_id

# Quantos IDs você quer gerar?
quantidade = 100  # Mude esse valor conforme o número de linhas da sua planilha

# Gera os IDs com sequência numérica
ids = [cria_id(sequencia=str(i + 1)) for i in range(quantidade)]

# Cria o DataFrame
df = pd.DataFrame({"ID": ids})

# Salva no Excel
df.to_excel("ids_gerados_para_colar.xlsx", index=False)

print("✅ Lista de IDs salva no arquivo 'ids_gerados_para_colar.xlsx'")
