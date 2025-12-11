# paginas/financeiro.py
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from funcoes_compartilhadas.conversa_banco import select, insert, delete


TABELA = "painel_financeiro"


def gerar_pdf(df, mes, total, comparacao):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    # LOGO DA EMPRESA
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo = os.path.join(BASE_DIR, "..", "imagens", "logo.png")

    pdf.drawImage(logo, 40, altura - 100, width=120, preserveAspectRatio=True, mask='auto')



    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, altura - 60, "RELATÓRIO FINANCEIRO MENSAL")

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
    df = select(TABELA, tipos_colunas={})

    


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

        resumo = df.groupby("Mes Computado")["Valor"].sum().sort_index()
        resumo.index = resumo.index.strftime("%m/%Y")

        fig, ax = plt.subplots()
        ax.plot(resumo.index, resumo.values, marker="o")

        ax.set_ylabel("Faturamento (R$)")
        ax.set_xlabel("Mês/Ano")
        ax.set_title("Evolução do faturamento")
        ax.grid(True)

        # RÓTULOS NOS PONTOS
        for x, y in zip(resumo.index, resumo.values):
            ax.annotate(
                f"R$ {y:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                (x, y),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=9
            )

        # SALVAR IMAGEM DO GRÁFICO
        grafico_buffer = BytesIO()
        fig.savefig(grafico_buffer, format="png", dpi=200, bbox_inches="tight")
        grafico_buffer.seek(0)

        # MOSTRAR NO SISTEMA
        st.pyplot(fig)

        # BOTÃO PARA BAIXAR IMAGEM
        st.download_button(
            label="🖼️ Baixar gráfico como imagem",
            data=grafico_buffer,
            file_name=f"grafico_faturamento_{mes_selecionado}.png",
            mime="image/png"
        )


        # ----------------------------------------------------
        # TABELA DO MÊS
        # ----------------------------------------------------
        st.subheader("📄 Lançamentos do mês")
        df_mes["Data"] = df_mes["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(df_mes[["Data", "Valor", "Observação"]])
        # ----------------------------------------------------
        # EXCLUIR LANÇAMENTO
        # ----------------------------------------------------
        st.subheader("🗑️ Excluir lançamento")

        df_mes["ID_TEMP"] = (
            df_mes["Data"].astype(str) + " | " +
            df_mes["Valor"].astype(str) + " | " +
            df_mes["Observação"].astype(str)
        )

        opcao = st.selectbox(
            "Selecione o lançamento para excluir",
            df_mes["ID_TEMP"].unique()
        )

        if st.button("❌ Excluir lançamento"):
            partes = opcao.split(" | ")
            data_sel = partes[0]
            valor_sel = partes[1]
            obs_sel = partes[2]

            delete(
                TABELA,
                where=f"Data,=,{data_sel}",
                tipos_colunas={}  # não tem escala aqui
            )

            st.success("✅ Lançamento excluído.")
            st.rerun()


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
        insert(TABELA, {
            "Data": data.strftime("%d/%m/%Y"),
            "Valor": valor,
            "Status": "Recebido",
            "Observação": obs
        })
        st.success("✅ Receita registrada com sucesso!")
        st.rerun()



def app():
    app_financeiro()
