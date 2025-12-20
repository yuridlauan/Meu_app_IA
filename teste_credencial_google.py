import json
import gspread
from google.oauth2.service_account import Credentials

# Caminho do arquivo de credenciais
CAMINHO_CREDENCIAL = "credenciais/gdrive_credenciais.json"

# Link da sua planilha (verifique se está certo!)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1et6jiVi7MhMTaXdVl7XV6yZx5-vaMz6p2eh1619Il20/edit"

# Carrega a credencial
with open(CAMINHO_CREDENCIAL, "r", encoding="utf-8") as f:
    credenciais_json = json.load(f)

# Define os escopos (permissões)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

try:
    # Faz a autenticação
    credenciais = Credentials.from_service_account_info(credenciais_json, scopes=SCOPES)
    gc = gspread.authorize(credenciais)

    # Tenta abrir a planilha
    planilha = gc.open_by_url(URL_PLANILHA)
    dados = planilha.sheet1.get_all_records()

    print("✅ Conexão bem-sucedida!")
    print("📄 Primeiras linhas da planilha:")
    for linha in dados[:5]:
        print(linha)

except Exception as e:
    print("❌ ERRO AO CONECTAR:")
    print(e)
