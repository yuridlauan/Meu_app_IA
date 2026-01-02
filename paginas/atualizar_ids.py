# 📁 atualizar_ids.py (dentro da pasta /paginas)

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random

# Função para criar ID único com sufixo aleatório
def criar_id():
    agora = datetime.now()
    sufixo = random.randint(1000, 9999)
    return agora.strftime("%Y%m%d_%H%M%S_127001_1") + f"_{sufixo}"

# Nome da planilha no Google Sheets
NOME_PLANILHA = "Banco de Dados"

# Abas válidas para atualização
ABAS_CIDADES = [
    "Porangatu", "Santa Tereza", "Estrela do Norte",
    "Formoso", "Trombas", "Novo Planalto",
    "Montividiu", "Mutunópolis"
]

def app():
    st.title("🔄 Atualizar IDs")
    st.write("Esse processo irá atualizar os IDs ausentes nas abas das cidades.")

    if st.button("🚀 Iniciar Atualização"):
        with st.spinner("🔄 Atualizando..."):
            try:
                # Autenticação
                escopos = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
                credenciais = Credentials.from_service_account_info(
                    st.secrets["gdrive_credenciais"],
                    scopes=escopos
                )
                cliente = gspread.authorize(credenciais)
                planilha = cliente.open(NOME_PLANILHA)

                total_inseridos = 0

                for aba in planilha.worksheets():
                    nome_aba = aba.title
                    if nome_aba not in ABAS_CIDADES:
                        continue

                    dados = aba.get_all_records()
                    if not dados:
                        continue

                    ids_existentes = aba.col_values(1)
                    atualizacoes = []

                    for i, _ in enumerate(dados):
                        id_valor = ids_existentes[i + 1] if i + 1 < len(ids_existentes) else ''
                        if not id_valor.strip():
                            novo_id = criar_id()
                            atualizacoes.append((i + 2, novo_id))  # linha real na planilha

                    for linha_idx, novo_id in atualizacoes:
                        aba.update_cell(linha_idx, 1, novo_id)

                    total_inseridos += len(atualizacoes)
                    if atualizacoes:
                        st.success(f"✅ {len(atualizacoes)} IDs atualizados na aba **{nome_aba}**")

                st.info(f"✅ Atualização concluída. Total de IDs adicionados: {total_inseridos}")
            except gspread.exceptions.APIError as api_err:
                st.error(f"Erro de API do Google Sheets: {api_err}")
            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}")
