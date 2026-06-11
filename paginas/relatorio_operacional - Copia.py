# paginas/relatorio_operacional.py

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

from funcoes_compartilhadas.conversa_banco import select

# ---------------------------------------------------
# CONFIGURAÇÕES
# ---------------------------------------------------

TIPOS_COLUNAS = {
    "ID": "id",
    "Data de Protocolo": "data",
    "Nº de Protocolo": "texto",
    "Tipo de Serviço": "texto",
    "CPF/CNPJ": "texto",
    "Nome Fantasia": "texto",
    "Área (m²)": "numero",
    "Notificação": "texto",
    "Validade do Boleto": "data",
    "Validade do Cercon": "data",
    "Tipo de Empresa": "texto",
    "Contato": "texto",
    "Militar Responsável": "texto",
    "Andamento": "texto",
    "Cidade": "texto"
}

# ---------------------------------------------------
# ABAS DO GOOGLE SHEETS
# ---------------------------------------------------

TABELAS = [
    "Porangatu",
    "Santa Tereza",
    "Estrela do Norte",
    "Formoso",
    "Trombas",
    "Novo Planalto",
    "Montividiu",
    "Mutunópolis"
]

# ---------------------------------------------------
# CARREGA TODOS OS DADOS
# ---------------------------------------------------
@st.cache_data(ttl=60)
def carregar_dados():


    lista_df = []

    for tabela in TABELAS:

        dados = select(
            tabela,
            TIPOS_COLUNAS
        )

        df_temp = pd.DataFrame(dados)

        if not df_temp.empty:
            lista_df.append(df_temp)

    if len(lista_df) == 0:
        return pd.DataFrame()

    return pd.concat(
        lista_df,
        ignore_index=True
    )


# ---------------------------------------------------
# APP
# ---------------------------------------------------

def app():

    st.title("📊 Relatório Operacional")

    df = carregar_dados()
    
    
    

    if df.empty:
        st.warning("Nenhum dado encontrado.")
        return

    # --------------------------------------------
    # DATAS
    # --------------------------------------------

    # ----------------------------------------------------
# TRATAMENTO DAS DATAS
# ----------------------------------------------------

    # Converte serial do Google Sheets para data real

    df["DataProt_dt"] = pd.to_datetime(
        pd.to_numeric(
            df["Data de Protocolo"],
            errors="coerce"
        ),
        unit="D",
        origin="1899-12-30"
    )
    
    df["Validade_dt"] = pd.to_datetime(
    pd.to_numeric(
        df["Validade do Cercon"],
        errors="coerce"
    ),
    unit="D",
    origin="1899-12-30"
)

    # Cria coluna de mês igual ao Financeiro

    df["Mes"] = df["DataProt_dt"].dt.strftime("%m/%Y")
    

    hoje = pd.Timestamp.today()
    # --------------------------------------------
    # FILTROS
    # --------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        cidades = sorted(
            df["Cidade"]
            .dropna()
            .unique()
            .tolist()
        )

        cidade = st.selectbox(
            "Cidade",
            ["Todas"] + cidades
        )

    with col2:

        meses = (
    df
    .assign(
        MesRef=df["DataProt_dt"].dt.to_period("M")
    )
    .sort_values(
        "MesRef",
        ascending=False
    )
    ["Mes"]
    .drop_duplicates()
    .tolist()
)

    if not meses:

        st.error("Nenhuma data válida encontrada.")
        st.stop()

    mes = st.selectbox(
        "Mês",
        meses
    )



    # --------------------------------------------
    # FILTRO CIDADE
    # --------------------------------------------

    if cidade != "Todas":

        df = df[
            df["Cidade"] == cidade
        ]

    # --------------------------------------------
    # FILTRO MÊS
    # --------------------------------------------

    df = df[
    df["Mes"] == mes
]

    # --------------------------------------------
    # RESUMO GERAL
    # --------------------------------------------

    protocolos = len(df)

    vistorias = len(
        df[
            df["Andamento"]
            == "Vistoria Feita"
        ]
    )

    cercons = len(
        df[
            df["Andamento"]
            == "Cercon Impresso"
        ]
    )

    nao_certificou = len(
        df[
            df["Andamento"]
            == "Não Certificou"
        ]
    )

    notificados = len(
        df[
            df["Notificação"]
            == "Notificado"
        ]
    )

    st.subheader("📌 Resumo Geral")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Protocolos",
        protocolos
    )

    c2.metric(
        "Vistorias",
        vistorias
    )

    c3.metric(
        "Cercons",
        cercons
    )

    c4.metric(
        "Não Certificou",
        nao_certificou
    )

    c5.metric(
        "Notificados",
        notificados
    )

    st.divider()

    # --------------------------------------------
    # PENDÊNCIAS
    # --------------------------------------------

    protocolados = len(
        df[
            df["Andamento"]
            == "Protocolado"
        ]
    )

    vistoria_sem_cercon = len(
        df[
            df["Andamento"]
            == "Vistoria Feita"
        ]
    )

    cercons_vencidos = len(
        df[
            df["Validade_dt"] < hoje
        ]
    )

    cercons_30 = len(
        df[
            (df["Validade_dt"] >= hoje) &
            (
                df["Validade_dt"]
                <= hoje + pd.Timedelta(days=30)
            )
        ]
    )

    st.subheader("🚨 Pendências")

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Protocolados sem vistoria",
        protocolados
    )

    p2.metric(
        "Vistorias sem Cercon",
        vistoria_sem_cercon
    )

    p3.metric(
        "Cercons vencidos",
        cercons_vencidos
    )

    p4.metric(
        "Vencem em 30 dias",
        cercons_30
    )

    # ---------------------------------------------------
    # TIPOS DE SERVIÇO
    # ---------------------------------------------------

    st.divider()

    st.subheader("📋 Tipos de Serviço")

    tipo_servico = st.selectbox(
        "Selecione o tipo de serviço",
        [
            "Todos",
            "Vistoria para Funcionamento",
            "Licenciamento Facilitado",
            "Análise de Projeto",
            "Substituição de Projeto",
            "Ponto de Referência",
            "Credenciamento Extintor/Brigada",
            "Denúncia"
        ]
    )

    df_servicos = df.copy()

    if tipo_servico != "Todos":

        df_servicos = df_servicos[
            df_servicos["Tipo de Serviço"]
            == tipo_servico
        ]
        df_servicos = df_servicos.copy()

    df_servicos["Data de Protocolo"] = (
        df_servicos["DataProt_dt"]
        .dt.strftime("%d/%m/%Y")
    )

    colunas_exibir = [
        "Data de Protocolo",
        "Nº de Protocolo",
        "Nome Fantasia",
        "Cidade",
        "Andamento"
    ]

    df_exibir = df_servicos[
        colunas_exibir
    ].copy()

    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True
    ) 

    # ---------------------------------------------------
    # LISTA DE PENDÊNCIAS
    # ---------------------------------------------------

    st.divider()

    st.subheader("🚨 Pendências")

    opcao_pendencia = st.selectbox(
        "Selecione a pendência",
        [
            "Protocolados sem vistoria",
            "Vistorias sem Cercon",
            "Cercons vencidos",
            "Cercons vencendo em 30 dias"
        ]
    )

    hoje = pd.Timestamp.today()

    # --------------------------------------------
    # FILTROS DAS PENDÊNCIAS
    # --------------------------------------------

    if opcao_pendencia == "Protocolados sem vistoria":

        df_pendencias = df[
            df["Andamento"] == "Protocolado"
        ]

    elif opcao_pendencia == "Vistorias sem Cercon":

        df_pendencias = df[
            df["Andamento"] == "Vistoria Feita"
        ]

    elif opcao_pendencia == "Cercons vencidos":

        df_pendencias = df[
            df["Validade_dt"] < hoje
        ]

    elif opcao_pendencia == "Cercons vencendo em 30 dias":

        df_pendencias = df[
            (df["Validade_dt"] >= hoje) &
            (
                df["Validade_dt"]
                <= hoje + pd.Timedelta(days=30)
            )
        ]

    else:

        df_pendencias = pd.DataFrame()

    # --------------------------------------------
    # TOTAL ENCONTRADO
    # --------------------------------------------

    st.caption(
        f"Total encontrado: {len(df_pendencias)}"
    )

        # --------------------------------------------
    # FORMATA DATA PARA EXIBIÇÃO
    # --------------------------------------------

    if not df_pendencias.empty:

        df_pendencias = df_pendencias.copy()

        df_pendencias["Data de Protocolo"] = (
            df_pendencias["DataProt_dt"]
            .dt.strftime("%d/%m/%Y")
        )

    # --------------------------------------------
    # COLUNAS EXIBIDAS
    # --------------------------------------------

    colunas_pendencias = [
        "Data de Protocolo",
        "Nº de Protocolo",
        "Nome Fantasia",
        "Cidade",
        "Militar Responsável",
        "Andamento"
    ]

    st.dataframe(
        df_pendencias[colunas_pendencias],
        use_container_width=True,
        hide_index=True
    )