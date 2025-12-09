# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, trata_tabelas

TABELA = "menus"
TIPOS = {
    "ID": "id",
    "Nome": "texto",
    "Ordem": "numero100",
}

def app():
    st.subheader("🗂️ Cadastro de Menus")

    trata_tabelas.gerenciar_estado_grid("cadastro_menus")

    # ▶️ Formulário Popover
    with st.popover("➕ Novo Menu"):
        with st.form("form_menu"):
            nome = st.text_input("Nome do Menu")
            ordem = st.number_input("Ordem no Menu", min_value=1, step=1)
            enviar = st.form_submit_button("Salvar")

            if enviar:
                if not nome:
                    st.error("❌ Preencha todos os campos.")
                else:
                    dado = {
                        "Nome": nome.strip(),
                        "Ordem": ordem,
                    }
                    conversa_banco.insert(TABELA, dado)
                    st.success("✅ Menu cadastrado com sucesso.")
                    st.cache_data.clear()
                    st.rerun()

    # ▶️ Grid de Menus
    df = conversa_banco.select(TABELA, TIPOS)
    if df.empty:
        st.warning("Nenhum menu cadastrado.")
        return

    st.subheader("Lista de Menus")

    visiveis = {"Nome": "Nome", "Ordem": "Ordem"}
    edit, ids = trata_tabelas.grid(df, visiveis, id_col="ID")

    trata_tabelas.salvar_edicoes(
        edit, df,
        ["Nome", "Ordem"],
        conversa_banco.update,
        TABELA, "ID", TIPOS,
    )

    trata_tabelas.opcoes_especiais(
        TABELA, ids,
        conversa_banco.delete,
        "ID", TIPOS,
    )
