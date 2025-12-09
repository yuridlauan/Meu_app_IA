# -*- coding: utf-8 -*-
# /paginas/relatorio_pdf.py

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

from funcoes_compartilhadas import conversa_banco, trata_tabelas
from funcoes_compartilhadas.estilos import set_page_title


# ─── Função para gerar PDF ─────────────────────────────────────────
def gerar_pdf(df, total_receitas, total_despesas, saldo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Financeiro", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Total Receitas: R$ {total_receitas:,.2f}", ln=True)
    pdf.cell(0, 8, f"Total Despesas: R$ {total_despesas:,.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo: R$ {saldo:,.2f}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(25, 8, "Data", 1)
    pdf.cell(40, 8, "Descrição", 1)
    pdf.cell(35, 8, "Categoria", 1)
    pdf.cell(30, 8, "Banco", 1)
    pdf.cell(25, 8, "Tipo", 1)
    pdf.cell(25, 8, "Valor", 1, ln=True)

    pdf.set_font("Arial", "", 9)

    for _, row in df.iterrows():
        pdf.cell(25, 8, str(row["Data"]), 1)
        pdf.cell(40, 8, str(row["Descricao"])[:25], 1)
        pdf.cell(35, 8, str(row["Categoria"])[:20], 1)
        pdf.cell(30, 8, str(row["Banco"])[:15], 1)
        pdf.cell(25, 8, str(row["Tipo"]), 1)
        valor = row["Valor"]
        pdf.cell(25, 8, f"R$ {valor:,.2f}", 1, ln=True)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return BytesIO(pdf_bytes)



# ─── Função Principal ──────────────────────────────────────────────
def app():
    set_page_title("Relatório em PDF")

    st.subheader("Relatório Financeiro")

    # ─── Leitura dos Dados ─────────────────────────────────────────
    TIPOS_COLUNAS = {
        "Data": "data",
        "Descricao": "texto",
        "Categoria": "texto",
        "Banco": "texto",
        "Valor": "numero100",
        "Tipo": "texto",
        "Status": "texto",
        "ID": "id",
    }

    df = conversa_banco.select("lancamentos", TIPOS_COLUNAS)

    # ─── Filtro ───────────────────────────────────────────────────
    df_filtrado = trata_tabelas.filtrar_tabela(
        df,
        ["Descricao", "Categoria", "Banco", "Status"],
        nome="relatorio"
    )

    if df_filtrado.empty:
        st.warning("Nenhum lançamento encontrado para o filtro selecionado.")
        return

    # 🔢 Aplica sinal negativo para Despesas
    df_filtrado["Valor"] = df_filtrado.apply(
        lambda row: -row["Valor"] if row["Tipo"] == "Despesa" else row["Valor"],
        axis=1
    )

    # ─── Resumo ───────────────────────────────────────────────────
    total_receitas = df_filtrado[df_filtrado["Tipo"] == "Receita"]["Valor"].sum()
    total_despesas = df_filtrado[df_filtrado["Tipo"] == "Despesa"]["Valor"].sum() * -1
    saldo = total_receitas - total_despesas

    st.subheader("Resumo Financeiro")
    st.write(f"🟢 **Total Receitas:** R$ {total_receitas:,.2f}")
    st.write(f"🔴 **Total Despesas:** R$ {total_despesas:,.2f}")
    st.write(f"💰 **Saldo:** R$ {saldo:,.2f}")

    # ─── Tabela ───────────────────────────────────────────────────
    st.subheader("Detalhamento dos Lançamentos")
    st.dataframe(df_filtrado, use_container_width=True)

    # ─── Gera PDF ─────────────────────────────────────────────────
    pdf_buffer = gerar_pdf(df_filtrado, total_receitas, total_despesas, saldo)

    st.download_button(
        label="📄 Baixar Relatório em PDF",
        data=pdf_buffer,
        file_name=f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
