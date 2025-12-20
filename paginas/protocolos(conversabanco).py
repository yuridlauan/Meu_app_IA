# -*- coding: utf-8 -*-
"""
Camada de acesso Google Sheets ↔ Pandas (GENÉRICA).

Escala numérica controlada por TIPOS_COLUNAS:
    - "numero"     → grava e lê como está
    - "numero100"  → grava ×100, lê ÷100
    - "id", "texto", "data" não sofrem ajuste

Quer trocar para MySQL? Basta reimplementar:
    → select, insert, update, delete
mantendo os mesmos parâmetros.
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import time
from functools import wraps
from gspread.exceptions import APIError
from funcoes_compartilhadas.cria_id import cria_id   # ⬅️ novo
from collections.abc import Mapping

# ===================================================
# 🔐 CREDENCIAIS E CONEXÃO COM PLANILHA
# ===================================================
import json

# ===================================================
# 🔐 CREDENCIAIS VIA STREAMLIT SECRETS
# ===================================================
# 🔐 CREDENCIAIS E CONEXÃO COM PLANILHA
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1et6jiVi7MhMTaXdVl7XV6yZx5-vaMz6p2eh1619Il20/edit"
_scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _carrega_credenciais():
    """
    Tenta carregar as credenciais a partir do secrets do Streamlit
    e faz parse caso venham como string JSON (cenário comum no deploy).
    """

    try:
        credenciais_brutas = st.secrets["gdrive_credenciais"]
    except Exception:
        # 🌐 Se falhar, usa arquivo local (modo desenvolvimento)
        try:
            with open("credenciais/gdrive_credenciais.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise RuntimeError(
                "⚠️ Credenciais do Google não encontradas. "
                "Defina `gdrive_credenciais` no secrets ou adicione credenciais/gdrive_credenciais.json"
            ) from e

    if isinstance(credenciais_brutas, str):
        try:
            return json.loads(credenciais_brutas)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                "⚠️ O secret `gdrive_credenciais` precisa ser JSON válido ou tabela TOML. "
                "No Streamlit Cloud, use a seção [gdrive_credenciais] em secrets ou cole o JSON completo."
            ) from e

    if isinstance(credenciais_brutas, dict):
        return dict(credenciais_brutas)

    raise RuntimeError(
        "⚠️ Formato de `gdrive_credenciais` inválido. Informe como objeto JSON ou mapa TOML."
    )


# 🔐 Autoriza acesso
_gc = gspread.authorize(
     Credentials.from_service_account_info(_carrega_credenciais(), scopes=_scopes)
)

# 🔗 Abre a planilha




# ===================================================
# ❗❗ RETENTATIVAS API
# ===================================================
def retry_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tentativas = 15  # 12×5 s + 3 extras
        with st.spinner("⏳ Aguardando servidor..."):
            for _ in range(tentativas):
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    if "Quota exceeded" in str(e):
                        time.sleep(5)
                    else:
                        raise e
        st.error("❌ Falha após múltiplas tentativas devido a limite de requisições.")
        raise APIError("Falha após múltiplas tentativas devido a quota excedida.")

    return wrapper


# ===================================================
# 🔢 AJUSTE DE ESCALA NUMÉRICA
# ===================================================
def _scale(df: pd.DataFrame, tipos: dict, modo: str) -> pd.DataFrame:
    """
    Ajusta escala e garante tipo numérico nas colunas cujo tipo começa por 'numero'.

    • Converte *qualquer* coluna 'numero*' em float.
    • Para tipo 'numero100':
        – modo 'mostrar' → divide por 100
        – modo 'gravar'  → multiplica por 100
    """
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        if tipo == "numero100":
            df[col] = df[col] if modo == "mostrar" else df[col] * 100
    return df


# ===================================================
# 🔧 FUNÇÕES AUXILIARES
# ===================================================
def _map_cols(df: pd.DataFrame) -> dict:
    """{coluna_minúscula: Coluna_Original}"""
    return {c.lower(): c for c in df.columns}


# _next_id mantido apenas para compatibilidade, mas não é mais utilizado.
def _next_id(_):  # deprecated
    return 0


# ===================================================
# 🟩 SELECT
# ===================================================
@retry_api_error
def select(tabela: str, tipos_colunas: dict) -> pd.DataFrame:
    ws = _sheet.worksheet(tabela)
    ws = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")
    df = pd.DataFrame(ws).rename(columns=str.strip)

    # 🔥 Proteção: se vazio, cria com as colunas certas
    if df.empty:
        df = pd.DataFrame(columns=tipos_colunas.keys())

    return _scale(df, tipos_colunas, "mostrar")


# ===================================================
# 🟦 INSERT
# ===================================================
@retry_api_error
def insert(tabela: str, dados):
    ws = _sheet.worksheet(tabela)

    # Padroniza entrada
    if isinstance(dados, pd.DataFrame):
        dados = dados.to_dict("records")
    if isinstance(dados, dict):
        dados = [dados]

    # Adiciona ID automático (string) se não existir
    for i, item in enumerate(dados, start=1):
        if not item.get("ID"):
            item["ID"] = cria_id(sequencia=str(i))

    df = pd.DataFrame(dados)

    # Cabeçalho (linha 1)
    header = ws.row_values(1) or list(df.columns)
    if not ws.row_values(1):
        ws.insert_row(header, 1)
    else:
        for c in df.columns:
            if c not in header:
                header.append(c)
        ws.update("A1", [header])

    # Linhas de dados
    linhas = [[r.get(h, "") for h in header] for r in df.to_dict("records")]
    ws.insert_rows(linhas, row=len(ws.get_all_values()) + 1)


# ===================================================
# 🟨 UPDATE
# ===================================================
@retry_api_error
def update(tabela: str, campos: list, valores: list, where: str, tipos_colunas: dict) -> int:
    ws = _sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    if tipos_colunas.get(real) == "numero100":
        try:
            alvo = str(float(alvo))
        except Exception:
            pass

    linhas = df.index[df[real].astype(str) == str(alvo)]
    if linhas.empty:
        return 0

    for lin in linhas:
        for c, v in zip(campos, valores):
            real_c = col_map[c.lower()]
            ws.update_cell(lin + 2, df.columns.get_loc(real_c) + 1, v)

    return len(linhas)


# ===================================================
# 🟥 DELETE
# ===================================================
@retry_api_error
def delete(tabela: str, where: str, tipos_colunas: dict) -> int:
    ws = _sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    if tipos_colunas.get(real) == "numero100":
        try:
            alvo = str(float(alvo))
        except Exception:
            pass

    linhas = df.index[df[real].astype(str) == str(alvo)]
    for i in sorted(linhas, reverse=True):
        ws.delete_rows(i + 2)

    return len(linhas)

    
def select_all(tipos_colunas):
    """
    Lê todas as abas da planilha e retorna um único DataFrame.
    """
    import pandas as pd

    planilha = _sheet  # já está aberto no seu código

    dados = []

    for worksheet in planilha.worksheets():

        nome_aba = worksheet.title

        try:
            df = pd.DataFrame(worksheet.get_all_records())

            if df.empty:
                continue

            # Garante todas as colunas esperadas
            for col in tipos_colunas:
                if col not in df.columns:
                    df[col] = ""

            df["Cidade"] = nome_aba  # reforça a origem
            dados.append(df)

        except Exception as e:
            print(f"Erro lendo aba {nome_aba}: {e}")

    if dados:
        return pd.concat(dados, ignore_index=True)

    return pd.DataFrame(columns=list(tipos_colunas.keys()))

import pandas as pd

def select_financeiro():
    import pandas as pd

    ws = _sheet.worksheet("painel_financeiro")
    dados = ws.get_all_records()

    df = pd.DataFrame(dados)

    colunas = ["Data", "Valor", "Status", "Observação"]
    for col in colunas:
        if col not in df.columns:
            df[col] = ""

    return df
# TESTE RÁPIDO PARA VER SE CONECTA
if __name__ == "__main__":
    TIPOS_USUARIOS = {
        "ID": "id",
        "Nome": "texto",
        "Email": "texto",
        "Senha": "texto",
    }

    try:
        df = select("usuarios", TIPOS_USUARIOS)
        print(df)

    except Exception as e:
        print("❌ Erro ao acessar a planilha:", e)


