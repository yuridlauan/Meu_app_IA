import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# Função para criar ID
def criar_id():
    agora = datetime.now()
    return agora.strftime("%Y%m%d_%H%M%S_127001_1")

# Nome da sua planilha no Google Sheets
NOME_PLANILHA = "meu banco de dados"

# Lista de abas (cidades) que devem ser atualizadas
ABAS_CIDADES = [
    "Porangatu", "Santa Tereza", "Estrela do Norte",
    "Formoso", "Trombas", "Novo Planalto",
    "Montividiu", "Mutunópolis"
]

def app():
    st.title("🔄 Atualizar IDs")
    st.write("Esse processo irá atualizar os IDs ausentes nas abas das cidades.")

    if st.button("🚀 Iniciar Atualização"):
        try:
            # Autenticação usando Streamlit Secrets
            escopos = ["https://www.googleapis.com/auth/spreadsheets"]
            credenciais = Credentials.from_service_account_info(
                st.secrets["gdrive_credenciais"],
                scopes=escopos
            )
            cliente = gspread.authorize(credenciais)

            planilha = cliente.open(NOME_PLANILHA)
            abas = planilha.worksheets()

            total_inseridos = 0

            for aba in abas:
                nome_aba = aba.title
                if nome_aba not in ABAS_CIDADES:
                    continue  # pula abas não relacionadas

                dados = aba.get_all_records()
                if not dados:
                    continue

                ids = aba.col_values(1)  # primeira coluna (ID)
                atualizacoes = []

                for i, linha in enumerate(dados):
                    if not ids[i + 1].strip():  # +1 para ignorar cabeçalho
                        novo_id = criar_id()
                        atualizacoes.append((i + 2, novo_id))  # +2 para linha real da planilha

                for linha_idx, novo_id in atualizacoes:
                    aba.update_cell(linha_idx, 1, novo_id)  # coluna 1 = A

                total_inseridos += len(atualizacoes)
                st.success(f"✅ {len(atualizacoes)} IDs atualizados na aba **{nome_aba}**")

            st.info(f"✅ Atualização concluída: {total_inseridos} IDs adicionados.")
        except Exception as e:
            st.error(f"Erro ao atualizar IDs: {e}")
