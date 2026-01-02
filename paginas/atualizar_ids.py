# 📁 atualizar_ids.py (dentro da pasta /paginas)

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random
import time

# Função para criar ID único
def criar_id():
    agora = datetime.now()
    sufixo = random.randint(1000, 9999)
    return agora.strftime("%Y%m%d_%H%M%S_127001_1") + f"_{sufixo}"

# Nome da planilha no Google Sheets
NOME_PLANILHA = "Banco de Dados"

# Abas válidas
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
                # Autenticação via secrets
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

                total_ids = 0

                for aba in planilha.worksheets():
                    nome = aba.title
                    if nome not in ABAS_CIDADES:
                        continue

                    # Evita excesso de leitura (define faixa manualmente)
                    valores = aba.get_values("A2:Z500")  # pega até 499 linhas
                    if not valores:
                        continue

                    atualizacoes = []
                    for i, linha in enumerate(valores):
                        if len(linha) == 0 or (len(linha) > 0 and linha[0].strip() == ""):
                            novo_id = criar_id()
                            atualizacoes.append((i + 2, novo_id))  # linha real da planilha

                    for linha_idx, novo_id in atualizacoes:
                        aba.update_cell(linha_idx, 1, novo_id)

                    total_ids += len(atualizacoes)
                    if atualizacoes:
                        st.success(f"✅ {len(atualizacoes)} IDs adicionados na aba **{nome}**")

                    # Pausa de segurança entre abas
                    time.sleep(1)

                st.info(f"✅ Atualização finalizada. Total de IDs criados: {total_ids}")

            except gspread.exceptions.APIError as api_err:
                st.error(f"Erro da API do Google: {api_err}")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")
