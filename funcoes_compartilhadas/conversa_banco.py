# -*- coding: utf-8 -*-
"""
Camada de acesso Google Sheets ↔ Pandas (GENÉRICA).
Safe para Streamlit Cloud, VS Code e ambiente local.
"""

import pandas as pd
import gspread
import streamlit as st
import time
import json
from functools import wraps
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError
from funcoes_compartilhadas.cria_id import cria_id

# ===================================================
# 🔐 CONFIGURAÇÕES
# ===================================================
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1et6jiVi7MhMTaXdVl7XV6yZx5-vaMz6p2eh1619Il20/edit"
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ===================================================
# 🔐 CREDENCIAIS (SAFE)
# ===================================================
def _carrega_credenciais():
    # Streamlit Cloud / VS Code
    if "gdrive_credenciais" in st.secrets:
        creds = st.secrets["gdrive_credenciais"]
        if not isinstance(creds, dict):
            raise RuntimeError("Formato inválido de gdrive_credenciais")
        return dict(creds)

    # Fallback local
    caminho = "credenciais/gdrive_credenciais.json"
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(
            "Credenciais Google não encontradas "
            "(nem em st.secrets nem em arquivo local)."
        )

# ===================================================
# 🔐 CLIENTES (LAZY LOAD)
# ===================================================
def _get_gspread_client():
    if "gspread_client" not in st.session_state:
        creds = Credentials.from_service_account_info(
            _carrega_credenciais(),
            scopes=_SCOPES
        )
        st.session_state["gspread_client"] = gspread.authorize(creds)
    return st.session_state["gspread_client"]

def _get_sheet():
    if "gspread_sheet" not in st.session_state:
        gc = _get_gspread_client()
        st.session_state["gspread_sheet"] = gc.open_by_url(URL_PLANILHA)
    return st.session_state["gspread_sheet"]

# ===================================================
# ❗ RETENTATIVAS API
# ===================================================
def retry_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tentativas = 10
        for _ in range(tentativas):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                if "Quota exceeded" in str(e):
                    time.sleep(5)
                else:
                    raise
        raise APIError("Falha após múltiplas tentativas (quota).")
    return wrapper

# ===================================================
# 🔢 AJUSTE DE ESCALA
# ===================================================
def _scale(df: pd.DataFrame, tipos: dict, modo: str) -> pd.DataFrame:
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        if tipo == "numero100":
            df[col] = df[col] if modo == "mostrar" else df[col] * 100
    return df

def _map_cols(df: pd.DataFrame) -> dict:
    return {c.lower(): c for c in df.columns}

# ===================================================
# 🟩 SELECT
# ===================================================
@retry_api_error
def select(tabela: str, tipos_colunas: dict) -> pd.DataFrame:
    sheet = _get_sheet()
    ws = sheet.worksheet(tabela)
    dados = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")
    df = pd.DataFrame(dados).rename(columns=str.strip)

    if df.empty:
        df = pd.DataFrame(columns=tipos_colunas.keys())

    return _scale(df, tipos_colunas, "mostrar")

# ===================================================
# 🟦 INSERT
# ===================================================
@retry_api_error
def insert(tabela: str, dados):
    sheet = _get_sheet()
    ws = sheet.worksheet(tabela)

    if isinstance(dados, pd.DataFrame):
        dados = dados.to_dict("records")
    if isinstance(dados, dict):
        dados = [dados]

    for i, item in enumerate(dados, start=1):
        if not item.get("ID"):
            item["ID"] = cria_id(sequencia=str(i))

    df = pd.DataFrame(dados)

    header = ws.row_values(1) or list(df.columns)
    if not ws.row_values(1):
        ws.insert_row(header, 1)
    else:
        for c in df.columns:
            if c not in header:
                header.append(c)
        ws.update("A1", [header])

    linhas = [[r.get(h, "") for h in header] for r in df.to_dict("records")]
    ws.insert_rows(linhas, row=len(ws.get_all_values()) + 1)

# ===================================================
# 🟨 UPDATE
# ===================================================
@retry_api_error
def update(tabela: str, campos: list, valores: list, where: str, tipos_colunas: dict) -> int:
    sheet = _get_sheet()
    ws = sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    df = _scale(df, tipos_colunas, "gravar")
    col_map = _map_cols(df)

    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    linhas = df.index[df[real].astype(str) == str(alvo)]
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
    sheet = _get_sheet()
    ws = sheet.worksheet(tabela)
    df = pd.DataFrame(ws.get_all_records()).rename(columns=str.strip)
    if df.empty:
        return 0

    col_map = _map_cols(df)
    campo, _, alvo = [s.strip() for s in where.split(",")]
    real = col_map[campo.lower()]

    linhas = df.index[df[real].astype(str) == str(alvo)]
    for i in sorted(linhas, reverse=True):
        ws.delete_rows(i + 2)

    return len(linhas)

# ===================================================
# 🟪 FINANCEIRO
# ===================================================
def select_financeiro():
    sheet = _get_sheet()
    ws = sheet.worksheet("painel_financeiro")
    df = pd.DataFrame(ws.get_all_records())

    for col in ["Data", "Valor", "Status", "Observação"]:
        if col not in df.columns:
            df[col] = ""

    return df
