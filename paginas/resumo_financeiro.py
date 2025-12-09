# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from funcoes_compartilhadas import conversa_banco
from funcoes_compartilhadas.estilos import set_page_title

# ─── CONFIGURAÇÃO DA TABELA ──────────────────────────────────────
TABELA = "lancamentos"
TIPOS = {
    "ID": "id",
    "Data": "data",
    "Valor": "numero100",
    "Tipo": "texto",  # Receita ou Despesa
    "Categoria": "texto",
    "Descricao": "texto",
}

# ─── FUNÇÃO PRINCIPAL DA PÁGINA ──────────────────────────────────
def app():
    set_page_title("Resumo Financeiro")

    # ─── BUSCA DADOS ─────────────────────────────────────────────
    df = conversa_banco.select(TABELA, TIPOS)

    if df.empty:
        st.warning("Nenhum lançamento encontrado.")
        return

    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")

    # ─── FILTRO DE PERÍODO ───────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        data_ini = st.date_input("📅 Data Início", value=df["Data"].min().date())
    with col2:
        data_fim = st.date_input("📅 Data Fim", value=df["Data"].max().date())

    df = df[(df["Data"].dt.date >= data_ini) & (df["Data"].dt.date <= data_fim)]

    if df.empty:
        st.info("Nenhum dado no período selecionado.")
        return

    # ─── KPIs ─────────────────────────────────────────────────────
    maior_valor = df["Valor"].max()
    menor_valor = df["Valor"].min()

    despesas = df[df["Tipo"].str.lower() == "despesa"]
    receitas = df[df["Tipo"].str.lower() == "receita"]

    maior_despesa = despesas["Valor"].max() if not despesas.empty else 0
    menor_despesa = despesas["Valor"].min() if not despesas.empty else 0
    soma_despesas = despesas["Valor"].sum()
    soma_receitas = receitas["Valor"].sum()
    saldo = soma_receitas - soma_despesas

    # ─── EXIBE KPIs ──────────────────────────────────────────────
    st.markdown("## 📊 Indicadores do Período")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi4, kpi5, kpi6 = st.columns(3)

    kpi1.metric("Maior Valor", f"R$ {maior_valor:,.2f}")
    kpi2.metric("Menor Valor", f"R$ {menor_valor:,.2f}")
    kpi3.metric("Maior Despesa", f"R$ {maior_despesa:,.2f}")
    kpi4.metric("Menor Despesa", f"R$ {menor_despesa:,.2f}")
    kpi5.metric("Total Despesas", f"R$ {soma_despesas:,.2f}")
    kpi6.metric("Total Receitas", f"R$ {soma_receitas:,.2f}")

    st.markdown(f"### 💰 Saldo do Período: **R$ {saldo:,.2f}**")

    # ─── SALDO ACUMULADO ─────────────────────────────────────────
    st.markdown("## 📈 Evolução do Saldo Acumulado")

    df = df.sort_values("Data")
    df["Valor_signed"] = df.apply(lambda x: x["Valor"] if x["Tipo"].lower() == "receita" else -x["Valor"], axis=1)
    df["Saldo Acumulado"] = df["Valor_signed"].cumsum()

    fig, ax = plt.subplots()
    ax.plot(df["Data"], df["Saldo Acumulado"], marker="o", linestyle="-")
    ax.set_title("Evolução do Saldo Acumulado")
    ax.set_xlabel("Data")
    ax.set_ylabel("Saldo Acumulado (R$)")
    ax.grid(True)

    st.pyplot(fig)
