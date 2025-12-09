# -*- coding: utf-8 -*-
# /paginas/bancos.py

import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, trata_tabelas
from funcoes_compartilhadas.estilos import set_page_title

# ─── Configurações da Tabela ───────────────────────────────────────
TABELA = "bancos"
TIPOS_COLUNAS = {
    "Nome": "texto",
    "Tipo": "texto",  # Ex.: Conta Corrente, Poupança, Carteira, etc.
    "ID": "id",
}

# ─── Função Principal ──────────────────────────────────────────────
def app():
    set_page_title("Gerenciar Bancos")
    trata_tabelas.gerenciar_estado_grid("bancos")

    # ─── Leitura dos Dados ─────────────────────────────────────────
    df = conversa_banco.select(TABELA, TIPOS_COLUNAS)

    # ─── Linha com botões Criar + Filtro ───────────────────────────
    col1, col2 = st.columns([1, 8])

    with col1:
        with st.popover("➕ Criar"):
            st.subheader("Adicionar Novo Banco")
            nome = st.text_input("Nome do Banco ou Conta")
            tipo = st.selectbox("Tipo de Conta", ["Conta Corrente", "Poupança", "Dinheiro", "Carteira", "Cartão", "Outro"])

            if st.button("💾 Salvar Banco"):
                if not nome:
                    st.warning("⚠️ Informe o nome do banco ou conta.")
                else:
                    novo = {"Nome": nome, "Tipo": tipo}
                    conversa_banco.insert(TABELA, novo)
                    st.success("✅ Banco salvo com sucesso!")
                    st.cache_data.clear()
                    st.rerun()

    with col2:
        df_vis = trata_tabelas.filtrar_tabela(df, ["Nome", "Tipo"], nome="bancos")

    # ─── Grid com os Dados ─────────────────────────────────────────
    st.subheader("Bancos Cadastrados")
    visiveis = {"Nome": "Nome do Banco ou Conta", "Tipo": "Tipo de Conta"}
    edit, ids = trata_tabelas.grid(df_vis, visiveis, id_col="ID")

    # ─── Salvar Edições ────────────────────────────────────────────
    trata_tabelas.salvar_edicoes(
        edit, df,
        ["Nome", "Tipo"],
        conversa_banco.update,
        TABELA, "ID", TIPOS_COLUNAS,
    )

    # ─── Opções (Deletar e Clonar) ─────────────────────────────────
    trata_tabelas.opcoes_especiais(
        TABELA, ids,
        conversa_banco.delete,
        "ID", TIPOS_COLUNAS,
        fn_insert=conversa_banco.insert,
    )
