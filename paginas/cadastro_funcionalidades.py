# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, trata_tabelas

TABELA = "funcionalidades"
TIPOS = {
    "ID": "id",
    "ID_Menu": "texto",
    "Nome": "texto",
    "Caminho": "texto",
}

def app():
    st.subheader("⚙️ Cadastro de Funcionalidades")

    trata_tabelas.gerenciar_estado_grid("cadastro_funcionalidades")

    # 🔍 Busca menus cadastrados
    df_menus = conversa_banco.select("menus", {
        "ID": "id", "Nome": "texto", "Ordem": "numero100"
    })

    if df_menus.empty:
        st.error("⚠️ Cadastre um menu antes.")
        st.stop()

    opcoes_menus = {
        f'{row["Nome"]} (ID {row["ID"]})': row["ID"]
        for _, row in df_menus.iterrows()
    }

    # ▶️ Formulário Popover
    with st.popover("➕ Nova Funcionalidade"):
        with st.form("form_func"):
            menu_selecionado = st.selectbox("Menu", list(opcoes_menus.keys()))
            nome = st.text_input("Nome da Funcionalidade")
            caminho = st.text_input("Caminho do Arquivo (sem .py)")

            enviar = st.form_submit_button("Salvar")

            if enviar:
                if not nome or not caminho:
                    st.error("❌ Preencha todos os campos.")
                else:
                    dado = {
                        "ID_Menu": opcoes_menus[menu_selecionado],
                        "Nome": nome.strip(),
                        "Caminho": caminho.strip(),
                    }
                    conversa_banco.insert(TABELA, dado)
                    st.success("✅ Funcionalidade cadastrada com sucesso.")
                    st.cache_data.clear()
                    st.rerun()

    # ▶️ Grid de Funcionalidades
    df = conversa_banco.select(TABELA, TIPOS)
    if df.empty:
        st.warning("Nenhuma funcionalidade cadastrada.")
        return

    st.subheader("Lista de Funcionalidades")

    visiveis = {"ID_Menu": "ID Menu", "Nome": "Nome", "Caminho": "Caminho"}
    edit, ids = trata_tabelas.grid(df, visiveis, id_col="ID")

    trata_tabelas.salvar_edicoes(
        edit, df,
        ["ID_Menu", "Nome", "Caminho"],
        conversa_banco.update,
        TABELA, "ID", TIPOS,
    )

    trata_tabelas.opcoes_especiais(
        TABELA, ids,
        conversa_banco.delete,
        "ID", TIPOS,
    )
