# 📁 paginas/atualizar_ids.py
# Atualização segura de IDs usando a MESMA conexão do app

import streamlit as st
from datetime import datetime
import random
from funcoes_compartilhadas.conversa_banco import _sheet

# --------------------------------------------------
# CONFIGURAÇÕES
# --------------------------------------------------

ABAS_CIDADES = [
    "Porangatu", "Santa Tereza", "Estrela do Norte",
    "Formoso", "Trombas", "Novo Planalto",
    "Montividiu", "Mutunópolis"
]

# --------------------------------------------------
# GERADOR DE ID
# --------------------------------------------------

def criar_id():
    agora = datetime.now()
    sufixo = random.randint(1000, 9999)
    return agora.strftime("%Y%m%d_%H%M%S_127001_1") + f"_{sufixo}"

# --------------------------------------------------
# APP
# --------------------------------------------------

def app():
    st.title("🔄 Atualizar IDs dos Protocolos")
    st.warning(
        "⚠️ Esta ação irá preencher IDs vazios.\n\n"
        "IDs já existentes NÃO serão alterados."
    )

    if not st.button("🚀 Atualizar IDs agora"):
        return

    total_geral = 0

    with st.spinner("Atualizando IDs..."):
        for nome_aba in ABAS_CIDADES:
            try:
                ws = _sheet.worksheet(nome_aba)
                valores = ws.get_all_values()

                if len(valores) <= 1:
                    continue  # só cabeçalho

                cabecalho = valores[0]

                if "ID" not in cabecalho:
                    st.error(f"❌ Aba {nome_aba} não possui coluna ID")
                    continue

                col_id = cabecalho.index("ID") + 1
                atualizados = 0

                for i in range(2, len(valores) + 1):
                    valor_id = ws.cell(i, col_id).value

                    if valor_id is None or str(valor_id).strip() == "":
                        novo_id = criar_id()
                        ws.update_cell(i, col_id, novo_id)
                        atualizados += 1
                        total_geral += 1

                if atualizados:
                    st.success(f"✅ {atualizados} IDs criados na aba **{nome_aba}**")

            except Exception as e:
                st.error(f"Erro na aba {nome_aba}: {e}")

    st.info(f"✅ Processo finalizado. Total de IDs criados: {total_geral}")
