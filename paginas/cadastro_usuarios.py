# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, trata_tabelas
from funcoes_compartilhadas.controle_acesso import hash_senha

TABELA = "usuarios"
TIPOS = {
    "ID": "id",
    "Nome": "texto",
    "Email": "texto",
    "Senha": "texto",
}

def app():
    st.subheader("👥 Cadastro de Usuários")

    trata_tabelas.gerenciar_estado_grid("cadastro_usuarios")

    # ▶️ Formulário Popover
    with st.popover("➕ Novo Usuário"):
        with st.form("form_usuario"):
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            senha_conf = st.text_input("Confirme a Senha", type="password")
            enviar = st.form_submit_button("Salvar")

            if enviar:
                if senha != senha_conf:
                    st.error("❌ Senhas não conferem.")
                elif not nome or not email or not senha:
                    st.error("❌ Preencha todos os campos.")
                else:
                    dado = {
                        "Nome": nome.strip(),
                        "Email": email.strip().lower(),
                        "Senha": hash_senha(senha.strip()),
                    }
                    conversa_banco.insert(TABELA, dado)
                    st.success("✅ Usuário cadastrado com sucesso.")
                    st.cache_data.clear()
                    st.rerun()

    # ▶️ Grid de Usuários
    df = conversa_banco.select(TABELA, TIPOS)
    if df.empty:
        st.warning("Nenhum usuário cadastrado.")
        return

    st.subheader("Lista de Usuários")

    visiveis = {"Nome": "Nome", "Email": "Email"}
    edit, ids = trata_tabelas.grid(df, visiveis, id_col="ID")

    trata_tabelas.salvar_edicoes(
        edit, df,
        ["Nome", "Email"],
        conversa_banco.update,
        TABELA, "ID", TIPOS,
    )

    trata_tabelas.opcoes_especiais(
        TABELA, ids,
        conversa_banco.delete,
        "ID", TIPOS,
    )
