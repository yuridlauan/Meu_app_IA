# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import date, timedelta

from paginas.protocolos import formulario_protocolo, TIPOS_COLUNAS
from funcoes_compartilhadas.conversa_banco import select, update, delete


# ---------------------------------------------------------
# LISTAR PROTOCOLOS EM UMA ABA
# ---------------------------------------------------------
def listar_protocolos(df_filtrado, TABELA, contexto):

    if df_filtrado.empty:
        st.info("Nenhum protocolo nesta categoria.")
        return

    for _, row in df_filtrado.iterrows():

        titulo = f"{row['Nº de Protocolo']} — {row['Nome Fantasia']}"
        cidade = row.get("Cidade", "")
        if cidade:
            titulo = f"{cidade} | {titulo}"

        with st.expander(titulo):

            prefix = f"{contexto}_{row['ID']}"
            dados = formulario_protocolo(row, prefix=prefix)

            confirma_key = f"confirma_{contexto}_{row['ID']}"
            if confirma_key not in st.session_state:
                st.session_state[confirma_key] = False

            with st.form(f"form_{contexto}_{row['ID']}"):
                c1, c2 = st.columns(2)
                atualizar = c1.form_submit_button("💾 Atualizar")
                excluir = c2.form_submit_button("🗑️ Excluir")

                if atualizar:
                    update(
                        TABELA,
                        list(dados.keys()),
                        list(dados.values()),
                        where=f"ID,eq,{row['ID']}",
                        tipos_colunas=TIPOS_COLUNAS
                    )
                    st.success("Atualizado!")
                    st.rerun()

                if excluir:
                    st.session_state[confirma_key] = True

            # Confirmação fora do form
            if st.session_state.get(confirma_key, False):
                st.warning("Tem certeza que deseja excluir?")
                col1, col2 = st.columns(2)

                if col1.button("Confirmar", key=f"del_{contexto}_{row['ID']}"):
                    delete(TABELA, where=f"ID,eq,{row['ID']}", tipos_colunas=TIPOS_COLUNAS)
                    st.success("Excluído!")
                    st.rerun()

                if col2.button("Cancelar", key=f"cancel_{contexto}_{row['ID']}"):
                    st.session_state[confirma_key] = False


# ---------------------------------------------------------
#  PÁGINA PRINCIPAL DO MILITAR
# ---------------------------------------------------------
def app(nome_militar, TABELA="Protocolos", admin=False):

    st.title(f"👨‍🚒 Painel de {nome_militar}")

    df = pd.DataFrame(select(TABELA, TIPOS_COLUNAS))

    if not admin:
        df = df[df["Militar Responsável"] == nome_militar]

    if df.empty:
        st.info("Nenhum protocolo encontrado.")
        return

    df["DataProt_dt"] = pd.to_datetime(
        df["Data de Protocolo"], dayfirst=True, errors="coerce"
    )

    hoje = date.today()
    semana = hoje - timedelta(days=7)

    df_novos = df[df["DataProt_dt"] >= pd.Timestamp(semana)]

    df_atr = df[df["Andamento"].isin(["Boleto Impresso", "Isento", "MEI"])]
    df_and = df[df["Andamento"].isin(["Boleto Pago", "Boleto Entregue"])]
    df_conc = df[df["Andamento"].isin(["Cercon Impresso", "Empresa Encerrou"])]
    df_pend = df[df["Andamento"].isin(["Processo Expirado", "Empresa Não Encontrada"])]

    aba_novos, aba_atr, aba_and, aba_conc, aba_pend = st.tabs([
        f"🆕 Novos (7 dias) ({len(df_novos)})",
        f"📘 Atribuídos ({len(df_atr)})",
        f"🟡 Em andamento ({len(df_and)})",
        f"🟢 Concluídos ({len(df_conc)})",
        f"🔴 Pendentes ({len(df_pend)})"
    ])

    with aba_novos:
        listar_protocolos(df_novos, TABELA, "novos")

    with aba_atr:
        listar_protocolos(df_atr, TABELA, "atr")

    with aba_and:
        listar_protocolos(df_and, TABELA, "and")

    with aba_conc:
        listar_protocolos(df_conc, TABELA, "conc")

    with aba_pend:
        listar_protocolos(df_pend, TABELA, "pend")

    if admin:
        st.divider()
        st.success("🛡️ Modo administrador ativo")
        st.caption("Acesso total aos protocolos, independentemente do militar.")
