# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import date, timedelta

from paginas.protocolos import formulario_protocolo, TIPOS_COLUNAS
from funcoes_compartilhadas.conversa_banco import select_all, update, delete, insert

# ---------------------------------------------------------
# LISTAR PROTOCOLOS EM UMA ABA
# ---------------------------------------------------------
def listar_protocolos(df_filtrado, TABELA, contexto):
    if df_filtrado.empty:
        st.info("Nenhum protocolo nesta categoria.")
        return

    for _, row in df_filtrado.iterrows():
        titulo = f"{row['Nº de Protocolo']} — {row['Nome Fantasia']}"
        cidade = row.get("Cidade", "")
        if cidade:
            titulo = f"{cidade} | {titulo}"

        with st.expander(titulo):
            id_linha = str(row["ID"]) if pd.notna(row["ID"]) else f"linha_{_}"
            prefix = f"{contexto}_{id_linha}"

            dados = formulario_protocolo(row, prefix=prefix)

            confirma_key = f"confirma_{contexto}_{row['ID']}"
            if confirma_key not in st.session_state:
                st.session_state[confirma_key] = False

            with st.form(f"form_{contexto}_{row['ID']}"):
                c1, c2 = st.columns(2)
                atualizar = c1.form_submit_button("💾 Atualizar")
                excluir = c2.form_submit_button("🗑️ Excluir")

                if atualizar:
                    for k in list(st.session_state.keys()):
                        if prefix in k:
                            del st.session_state[k]

                    update(
                        row["Cidade"],
                        list(dados.keys()),
                        list(dados.values()),
                        where=f"ID,eq,{row['ID']}",
                        tipos_colunas=TIPOS_COLUNAS
                    )
                    st.success("✅ Atualizado com sucesso!")
                    st.rerun()

                if excluir:
                    st.session_state[confirma_key] = True

            if st.session_state.get(confirma_key, False):
                st.warning("Tem certeza que deseja excluir?")
                col1, col2 = st.columns(2)

                if col1.button("Confirmar", key=f"del_{contexto}_{row['ID']}"):
                    delete(
                        row["Cidade"],
                        where=f"ID,eq,{row['ID']}",
                        tipos_colunas=TIPOS_COLUNAS
                    )
                    st.success("Excluído!")
                    st.rerun()

                if col2.button("Cancelar", key=f"cancel_{contexto}_{row['ID']}"):
                    st.session_state[confirma_key] = False

# ---------------------------------------------------------
# PÁGINA PRINCIPAL DO MILITAR
# ---------------------------------------------------------
def app(nome_militar, TABELA="Protocolos", admin=False):
    st.title(f"👨‍🚒 Painel de {nome_militar}")

    termo = st.text_input("🔍 Buscar protocolo (por nome, CPF, militar, tipo...)", placeholder="")

    df = select_all(TIPOS_COLUNAS)

    if not admin:
        df = df[df["Militar Responsável"] == nome_militar]

    if termo:
        termo = termo.lower()
        df = df[df.apply(lambda r: termo in str(r.values).lower(), axis=1)]

    if df.empty:
        st.info("Nenhum protocolo encontrado.")
        

    df["DataProt_dt"] = pd.to_datetime(df["Data de Protocolo"], dayfirst=True, errors="coerce")
    hoje = pd.Timestamp.today().normalize()
    sete_dias_atras = hoje - pd.Timedelta(days=7)


    df_atr = df[df["Militar Responsável"] == nome_militar]

    # 🔒 Controle de IDs já exibidos para evitar repetições nas abas
    ids_exibidos = set()

    # 🟡 Em andamento
    df_and = df_atr[
        df_atr["Andamento"].isin(["Protocolado", "Vistoria Feita"]) &
        (~df_atr["ID"].isin(ids_exibidos))
    ]
    ids_exibidos.update(df_and["ID"])

    # 🟢 Concluídos
    df_conc = df_atr[
        df_atr["Andamento"].isin(["Cercon Impresso", "Empresa Encerrou"]) &
        (~df_atr["ID"].isin(ids_exibidos))
    ]
    ids_exibidos.update(df_conc["ID"])

    # 🔴 Pendentes
    df_pend = df_atr[
        (df_atr["Andamento"] == "Empresa/Proprietário Não Localizado") &
        (~df_atr["ID"].isin(ids_exibidos))
    ]
    ids_exibidos.update(df_pend["ID"])

    # 🆕 Novos atribuídos nos últimos 7 dias
    df_novos = df_atr[
    (df_atr["DataProt_dt"].notna()) &
    (df_atr["DataProt_dt"] >= sete_dias_atras) &
    (~df_atr["ID"].isin(ids_exibidos))
]






    aba_eventos, aba_est, aba_novos, aba_and, aba_conc, aba_pend = st.tabs([
    f"📅 Eventos",
    f"📊 Estatísticas",
    f"🆕 Novos (7 dias) ({len(df_novos)})",
    f"🟡 Em andamento ({len(df_and)})",
    f"🟢 Concluídos ({len(df_conc)})",
    f"🔴 Pendentes ({len(df_pend)})"
])



    with aba_eventos:
        st.subheader("📅 Agenda de Eventos (por mês)")
        data_escolhida = st.date_input(
            "Selecione uma data (usada como referência para o mês):",
            date.today(),
            format="DD/MM/YYYY"
        )


        with st.popover("➕ Novo Evento"):
                with st.form("form_evento"):
                    titulo = st.text_input("Título do Evento")
                    descricao = st.text_area("Descrição (opcional)")
                    enviar = st.form_submit_button("Salvar")
                    if enviar:
                        if not titulo.strip():
                            st.warning("Informe um título para o evento.")
                        else:
                            evento = {
                                "Data": data_escolhida.strftime("%d/%m/%Y"),
                                "Título": titulo.strip(),
                                "Descrição": descricao.strip(),
                            }
                            insert("eventos", evento)
                            st.success("✅ Evento salvo com sucesso!")
                            st.cache_data.clear()
                            st.rerun()

        
        from funcoes_compartilhadas.conversa_banco import select

        # Lê os dados da aba "eventos"
        df_eventos = select(
            "eventos",
            {
                "ID": "id",
                "Data": "data",
                "Título": "texto",
                "Descrição": "texto"
            }
        )


        if not df_eventos.empty:
            df_eventos["Data_dt"] = pd.to_datetime(df_eventos["Data"], dayfirst=True, errors="coerce")
            mes = data_escolhida.month
            ano = data_escolhida.year

            eventos_do_mes = df_eventos[
                (df_eventos["Data_dt"].dt.month == mes) &
                (df_eventos["Data_dt"].dt.year == ano)
            ]

            if eventos_do_mes.empty:
                st.info("Nenhum evento neste mês.")
            else:
                st.write("### 📌 Eventos do mês")

                for _, linha in eventos_do_mes.iterrows():
                    col1, col2 = st.columns([5, 1])

                    with col1:
                        st.markdown(f"📅 **{linha['Data']} — {linha['Título']}**")
                        if linha["Descrição"]:
                            st.caption(linha["Descrição"])

                    with col2:
                        if st.button("🗑️", key=f"del_evt_{linha['ID']}"):
                            delete(
                                "eventos",
                                where=f"ID,eq,{linha['ID']}",
                                tipos_colunas={
                                    "ID": "id",
                                    "Data": "data",
                                    "Título": "texto",
                                    "Descrição": "texto"
                                }
                            )
                            st.success("✅ Evento excluído!")
                            st.rerun()


    # TABS EXISTENTES
    with aba_novos:
        listar_protocolos(df_novos, TABELA, "novos")
    with aba_and:
        listar_protocolos(df_and, TABELA, "andamento")
    with aba_conc:
        listar_protocolos(df_conc, TABELA, "concluido")
    with aba_pend:
        listar_protocolos(df_pend, TABELA, "pendente")
    with aba_est:
        st.subheader(f"📊 Evolução Mensal dos Protocolos — {nome_militar}")

        import matplotlib.pyplot as plt
        import numpy as np

        df_grafico = df.copy()
        df_grafico["DataProt_dt"] = pd.to_datetime(df_grafico["Data de Protocolo"], dayfirst=True, errors="coerce")
        df_grafico["Mês"] = df_grafico["DataProt_dt"].dt.strftime("%m - %B")

        andamento_map = {
        "Em andamento": ["Protocolado", "Vistoria Feita"],
        "Concluídos": ["Cercon Impresso", "Empresa Encerrou"],
        "Pendentes": ["Empresa/Proprietário Não Localizado"],
    }


        resumo = pd.DataFrame()

        for nome_categoria, status_lista in andamento_map.items():
            temp = df_grafico[df_grafico["Andamento"].isin(status_lista)]
            contagem = temp.groupby("Mês").size().rename(nome_categoria)
            resumo = pd.concat([resumo, contagem], axis=1)

        resumo = resumo.fillna(0).astype(int).sort_index()

        if resumo.empty:
            st.info("Ainda não há dados suficientes para gerar o gráfico.")
        else:
            if "pagina_est" not in st.session_state:
                st.session_state["pagina_est"] = 0

            total = len(resumo)
            inicio = st.session_state["pagina_est"] * 3
            fim = inicio + 3

            col1, col2, col3 = st.columns([1, 10, 1])
            with col1:
                if st.button("⬅️", disabled=inicio == 0):
                    st.session_state["pagina_est"] -= 1
            with col3:
                if st.button("➡️", disabled=fim >= total):
                    st.session_state["pagina_est"] += 1

            dados = resumo.iloc[inicio:fim]
            meses = dados.index.tolist()
            x = np.arange(len(meses))  # posições no eixo x
            largura = 0.25  # largura de cada barra

            fig, ax = plt.subplots(figsize=(8, 5))

            # Cria cada conjunto de barras com deslocamento
            ax.bar(x - largura, dados["Em andamento"], width=largura, label="Em andamento", color="gold")
            ax.bar(x, dados["Concluídos"], width=largura, label="Concluídos", color="green")
            ax.bar(x + largura, dados["Pendentes"], width=largura, label="Pendentes", color="red")

            ax.set_ylabel("Quantidade de Protocolos")
            ax.set_title("Evolução Mensal (últimos registros)")
            ax.set_xticks(x)
            ax.set_xticklabels(meses, rotation=45)
            ax.legend(loc="upper left")
            ax.set_yticks(np.arange(0, max(dados.max()) + 10, 10))  # escala de 10 em 10 no Y

            st.pyplot(fig)



    
