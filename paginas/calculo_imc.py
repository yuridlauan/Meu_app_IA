# paginas/financeiro.py
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from funcoes_compartilhadas.conversa_banco import select_financeiro, insert


TABELA = "financeiro"


def gerar_pdf(df, mes, total, comparacao):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altura - 50, "RELATÓRIO FINANCEIRO MENSAL")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, altura - 90, f"Mês/Ano: {mes}")
    pdf.drawString(50, altura - 120, f"Total arrecadado: R$ {total:,.2f}")
    pdf.drawString(50, altura - 150, f"Comparação com mês anterior: {comparacao}")

    pdf.drawString(50, altura - 190, "Lançamentos:")

    y = altura - 220
    for _, row in df.iterrows():
        linha = f"{row['Data']} | R$ {row['Valor']:,.2f} | {row['Observação']}"
        pdf.drawString(50, y, linha)
        y -= 18
        if y < 50:
            pdf.showPage()
            y = altura - 50

    pdf.save()
    buffer.seek(0)
    return buffer


def app_financeiro():

    st.title("💼 Painel Financeiro do Administrador")
    st.divider()

    # ----------------------------------------------------
    # CARREGAR DADOS
    # ----------------------------------------------------
    df = select_financeiro()
    


    if df.empty:
        df = pd.DataFrame(columns=["Data", "Valor", "Status", "Observação"])

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

    # ----------------------------------------------------
    # SELETOR DE MÊS
    # ----------------------------------------------------
    # ----------------------------------------------------
# SELETOR DE MÊS
# ----------------------------------------------------
    st.subheader("📆 Selecionar mês")
    df["Mes Computado"] = df["Data"].dt.to_period("M")
    df["Mes"] = df["Mes Computado"].dt.strftime("%m/%Y")
    meses = sorted(df["Mes"].dropna().unique(), reverse=True)


    mes_selecionado = None
    total_mes = 0
    df_mes = pd.DataFrame()

    if not meses:
        st.warning("⚠️ Nenhum lançamento financeiro encontrado ainda.")
        st.info("Use o formulário abaixo para inserir a primeira receita.")
        st.divider()
        mostrar_painel = False
    else:
        mostrar_painel = True

    # ----------------------------------------------------
    # PAINEL COMPLETO
    # ----------------------------------------------------
    if mostrar_painel:

        mes_selecionado = st.selectbox("Escolha o mês", meses)

        df_mes = df[df["Mes"] == mes_selecionado]
        total_mes = df_mes["Valor"].sum()

        # ----------------------------------------------------
        # COMPARAÇÃO COM MÊS ANTERIOR
        # ----------------------------------------------------
        indice = meses.index(mes_selecionado)
        total_anterior = 0

        if indice + 1 < len(meses):
            mes_anterior = meses[indice + 1]
            total_anterior = df[df["Mes"] == mes_anterior]["Valor"].sum()
        else:
            mes_anterior = "Não disponível"

        diferenca = total_mes - total_anterior
        percentual = (diferenca / total_anterior * 100) if total_anterior != 0 else 0

        # ----------------------------------------------------
        # INDICADORES
        # ----------------------------------------------------
        col1, col2, col3 = st.columns(3)
        col1.metric("Total do mês", f"R$ {total_mes:,.2f}")
        col2.metric("Mês anterior", f"R$ {total_anterior:,.2f}")
        col3.metric("Variação (%)", f"{percentual:.2f}%", delta=f"R$ {diferenca:,.2f}")

        # ----------------------------------------------------
        # GRÁFICO COMPARATIVO
        # ----------------------------------------------------
        st.subheader("📊 Comparativo mensal")

        resumo = df.groupby("Mes Computado")["Valor"].sum()
        resumo.index = resumo.index.astype(str).str[5:7] + "/" + resumo.index.astype(str).str[:4]


        fig, ax = plt.subplots()
        resumo.plot(kind="bar", ax=ax)
        ax.set_ylabel("Valor (R$)")
        ax.set_title("Arrecadação por mês")
        st.pyplot(fig)

        # ----------------------------------------------------
        # TABELA DO MÊS
        # ----------------------------------------------------
        st.subheader("📄 Lançamentos do mês")
        df_mes["Data"] = df_mes["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(df_mes[["Data", "Valor", "Observação"]])

        # ----------------------------------------------------
        # EXPORTAR EXCEL
        # ----------------------------------------------------
        buffer = BytesIO()
        df_mes.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button("⬇️ Exportar Excel", buffer, file_name=f"financeiro_{mes_selecionado}.xlsx")

        # ----------------------------------------------------
        # EXPORTAR PDF
        # ----------------------------------------------------
        comparacao = f"{percentual:.2f}% em relação ao mês anterior"

        pdf = gerar_pdf(df_mes, mes_selecionado, total_mes, comparacao)

        st.download_button(
            "📄 Gerar PDF mensal",
            pdf,
            file_name=f"relatorio_{mes_selecionado}.pdf",
            mime="application/pdf"
        )

            # ----------------------------------------------------
    # LANÇAMENTO SEMANAL (SEMPRE VISÍVEL)
    # ----------------------------------------------------
    st.divider()
    st.subheader("➕ Adicionar nova receita")

    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", format="DD/MM/YYYY")
    with col2:
        valor = st.number_input("Valor recebido", min_value=0.0)

    obs = st.text_input("Observação")

    if st.button("Salvar Receita"):
        insert("painel_financeiro", {
            "Data": data.strftime("%d/%m/%Y"),
            "Valor": valor,
            "Status": "Recebido",
            "Observação": obs
        })
        st.success("✅ Receita registrada com sucesso!")
        st.rerun()



def app():
    app_financeiro()
