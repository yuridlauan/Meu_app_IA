# -*- coding: utf-8 -*-
# /paginas/lancamentos.py

import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco, trata_tabelas
from funcoes_compartilhadas.estilos import set_page_title

# ─── Configurações da Tabela ───────────────────────────────────────
TABELA = "lancamentos"
TIPOS_COLUNAS = {
    "Data": "data",
    "Descricao": "texto",
    "Categoria": "texto",
    "Banco": "texto",
    "Valor": "numero100",
    "Tipo": "texto",    # Receita ou Despesa — puxado da categoria
    "Status": "texto",  # Pendente ou Realizado
    "ID": "id",
}

# ─── Função Principal ──────────────────────────────────────────────
def app():
    set_page_title("Lançamentos Financeiros")
    trata_tabelas.gerenciar_estado_grid("lancamentos")

    # ─── Leitura dos Dados ─────────────────────────────────────────
    df = conversa_banco.select(TABELA, TIPOS_COLUNAS)

    # ─── Leitura das Categorias e Bancos ───────────────────────────
    categorias = conversa_banco.select("categorias", {"Nome": "texto", "Tipo": "texto", "ID": "id"})
    bancos = conversa_banco.select("bancos", {"Nome": "texto", "Tipo": "texto", "ID": "id"})

    lista_categorias = categorias["Nome"].tolist() if not categorias.empty else []
    lista_bancos = bancos["Nome"].tolist() if not bancos.empty else []

    # ─── Linha com botões Criar + Filtro ───────────────────────────
    col1, col2 = st.columns([1, 8])

    with col1:
        with st.popover("➕ Criar"):
            st.subheader("Novo Lançamento")

            data = st.date_input("Data")
            descricao = st.text_input("Descrição")
            categoria = st.selectbox("Categoria", lista_categorias)
            banco = st.selectbox("Banco", lista_bancos)
            valor = st.number_input("Valor (R$)", 0.0, format="%.2f")
            status = st.selectbox("Status", ["Pendente", "Realizado"])

            # 🔥 Busca o Tipo baseado na Categoria
            tipo = ""
            if categoria:
                tipo = categorias.loc[categorias["Nome"] == categoria, "Tipo"].values[0]

            if st.button("💾 Salvar Lançamento"):
                if not descricao or not categoria or not banco:
                    st.warning("⚠️ Preencha todos os campos obrigatórios.")
                else:
                    novo = {
                        "Data": data.strftime("%d/%m/%Y"),
                        "Descricao": descricao,
                        "Categoria": categoria,
                        "Banco": banco,
                        "Valor": round(valor, 2),
                        "Tipo": tipo,
                        "Status": status,
                    }
                    conversa_banco.insert(TABELA, novo)
                    st.success("✅ Lançamento salvo com sucesso!")
                    st.cache_data.clear()
                    st.rerun()

    with col2:
        df_vis = trata_tabelas.filtrar_tabela(
            df,
            ["Descricao", "Categoria", "Banco", "Status"],
            nome="lancamentos"
        )

    # 🔢 Aplica sinal negativo para Despesas na visualização
    if not df_vis.empty:
        df_vis["Valor"] = df_vis.apply(
            lambda row: -row["Valor"] if row["Tipo"] == "Despesa" else row["Valor"],
            axis=1
        )

    # ─── Grid com os Dados ─────────────────────────────────────────
    st.subheader("Lançamentos Financeiros")
    visiveis = {
        "Data": "Data",
        "Descricao": "Descrição",
        "Categoria": st.column_config.SelectboxColumn(
            "Categoria", options=lista_categorias, required=True
        ),
        "Banco": st.column_config.SelectboxColumn(
            "Banco", options=lista_bancos, required=True
        ),
        "Tipo": "Tipo",
        "Status": st.column_config.SelectboxColumn(
            "Status", options=["Pendente", "Realizado"], required=True
        ),
        "Valor": "Valor (R$)"
    }

    edit, ids = trata_tabelas.grid(df_vis, visiveis, id_col="ID")

    # ─── Salvar Edições ────────────────────────────────────────────
    trata_tabelas.salvar_edicoes(
        edit, df,
        ["Data", "Descricao", "Categoria", "Banco", "Valor", "Status"],
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
