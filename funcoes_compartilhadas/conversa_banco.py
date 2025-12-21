# -*- coding: utf-8 -*-
"""
Camada de acesso Google Sheets ↔ Pandas (via Streamlit Secrets)
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import time
from functools import wraps
from gspread.exceptions import APIError
from funcoes_compartilhadas.cria_id import cria_id

# ===================================================
# 🔐 CREDENCIAIS E CONEXÃO COM PLANILHA
# ===================================================

# Lê as credenciais direto do secrets.toml
credenciais_info = st.secrets["gdrive_credenciais"]

# Define escopos de acesso
_scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Autoriza com base nas credenciais do secrets
_gc = gspread.authorize(
    Credentials.from_service_account_info(credenciais_info, scopes=_scopes)
)

# Abra a planilha pelo link (coloque direto no código, ou puxe de outro segredo)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1VxlCps0qSck915fqav1fUGDTtXI82CFI8MZaBEJ8vtI/edit"
_sheet = _gc.open_by_url(URL_PLANILHA)

# ===================================================
# ❗❗ RETENTATIVAS API
# ===================================================
def retry_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tentativas = 15
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
# 🔢 ESCALA NUMÉRICA
# ===================================================
def _scale(df: pd.DataFrame, tipos: dict, modo: str) -> pd.DataFrame:
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        if tipo == "numero100":
            df[col] = df[col] if modo == "mostrar" else df[col] * 100
    return df

# ===================================================
# 🔧 MAPEIA NOMES DE COLUNAS
# ===================================================
def _map_cols(df: pd.DataFrame) -> dict:
    return {c.lower(): c for c in df.columns}

# ===================================================
# 🟩 SELECT
# ===================================================
@retry_api_error
def select(tabela: str, tipos_colunas: dict) -> pd.DataFrame:
    ws = _sheet.worksheet(tabela)
    ws = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")
    df = pd.DataFrame(ws).rename(columns=str.strip)
    return _scale(df, tipos_colunas, "mostrar")

# ===================================================
# 🟦 INSERT
# ===================================================
@retry_api_error
def insert(tabela: str, dados):
    ws = _sheet.worksheet(tabela)
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
