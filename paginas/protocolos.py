# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import math
from funcoes_compartilhadas.conversa_banco import select, insert, update, delete
from funcoes_compartilhadas.cria_id import cria_id

# -----------------------------------------------------------
#                CONFIGURAÇÕES INICIAIS
# -----------------------------------------------------------

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

# -----------------------------------------------------------
#                 FUNÇÕES AUXILIARES
# -----------------------------------------------------------

def sanitize_number(value, default=0.0):
    try:
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        value = float(value)
        if math.isnan(value):
            return default
        return value
    except (ValueError, TypeError):
        return default


def carregar_dados(TABELA):
    def corrige_data(valor):
        try:
            if pd.isna(valor) or str(valor).strip() == "":
                return ""
            # formato numero tipo 45617 (excel serial)
            if str(valor).isdigit():
                data = pd.to_datetime("1899-12-30") + pd.to_timedelta(int(valor), unit="D")
                return data.strftime("%d/%m/%Y")
            else:
                data = pd.to_datetime(str(valor), dayfirst=True, errors="coerce")
                if pd.notna(data):
                    return data.strftime("%d/%m/%Y")
                return str(valor)
        except Exception:
            return str(valor)

    df = select(TABELA, TIPOS_COLUNAS)
    df = pd.DataFrame(df)

    for coluna in ["Data de Protocolo", "Validade do Boleto", "Validade do Cercon"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(corrige_data)

    return df


# -----------------------------------------------------------
#                 FORMULÁRIO DE PROTOCOLOS
# -----------------------------------------------------------

def formulario_protocolo(dados=None, prefix=""):
    """Formulário usado tanto para novo protocolo quanto para edição."""
    if dados is None:
        hoje = date.today()
        dados = {
            "Data de Protocolo": hoje.strftime("%d/%m/%Y"),
            "Nº de Protocolo": "",
            "Tipo de Serviço": "Vistoria para Funcionamento",
            "CPF/CNPJ": "",
            "Nome Fantasia": "",
            "Área (m²)": 0.0,
            "Notificação": "Notificar",
            "Validade do Boleto": (hoje + timedelta(days=30)).strftime("%d/%m/%Y"),
            "Validade do Cercon": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"),
            "Tipo de Empresa": "Regular",
            "Contato": "",
            "Militar Responsável": "Asp Of D'Lauan",
            "Andamento": "Protocolado",

        }

    col1, col2 = st.columns(2)

    # -------- COLUNA 1 --------
    with col1:
        data_raw = st.text_input(
            "Data de Protocolo (dd/mm/aaaa)",
            value=dados["Data de Protocolo"],
            key=f"data_{prefix}"
        )

        protocolo = st.text_input(
            "Nº de Protocolo",
            value=dados["Nº de Protocolo"],
            key=f"prot_{prefix}"
        )

        opcoes_tipo = [
            "Vistoria para Funcionamento",
            "Licenciamento Facilitado",
            "Análise de Projeto",
            "Substituição de Projeto", 
            "Ponto de Referência",
            "Credenciamento Extintor/Brigada"
        ]

        # descobre o índice correto com base no que veio do banco
        tipo_valor = dados.get("Tipo de Serviço", opcoes_tipo[0])
        if tipo_valor in opcoes_tipo:
            tipo_index = opcoes_tipo.index(tipo_valor)
        else:
            tipo_index = 0  # fallback

        tipo = st.selectbox(
            "Tipo de Serviço",
            opcoes_tipo,
            index=tipo_index,
            key=f"tipo_{prefix}"
        )


        cpf = st.text_input("CPF/CNPJ", value=dados["CPF/CNPJ"], key=f"cpf_{prefix}")
        nome = st.text_input("Nome Fantasia", value=dados["Nome Fantasia"], key=f"nome_{prefix}")

        area = st.number_input(
            "Área (m²)",
            min_value=0.0,
            format="%.2f",
            value=float(dados.get("Área (m²)", 0.0)),
            key=f"area_{prefix}"
        )

        notificacoes_opcoes = ["Notificado", "Notificar"]

        notificacao_valor = dados.get("Notificação", notificacoes_opcoes[1])
        if notificacao_valor in notificacoes_opcoes:
            notificacao_index = notificacoes_opcoes.index(notificacao_valor)
        else:
            notificacao_index = 1

        notificacao = st.selectbox(
            "Notificação",
            notificacoes_opcoes,
            index=notificacao_index,
            key=f"notif_{prefix}"
        )


   

    # -------- COLUNA 2 --------
    with col2:
        # Base para datas automáticas
        try:
            data_dt = datetime.strptime(data_raw, "%d/%m/%Y")
        except ValueError:
            data_dt = None

        # Validade do Boleto = data protocolo + 30 dias
        if data_dt:
            validade_boleto_auto = (data_dt + timedelta(days=30)).strftime("%d/%m/%Y")
        else:
            validade_boleto_auto = dados.get("Validade do Boleto", "")

        validade_boleto = st.text_input(
            "Validade do Boleto (dd/mm/aaaa)",
            value=validade_boleto_auto,
            key=f"valboleto_{prefix}"
        )

        # Validade do Cercon = data protocolo + 365 dias
        if data_dt:
            validade_cercon_auto = (data_dt + timedelta(days=365)).strftime("%d/%m/%Y")
        else:
            validade_cercon_auto = dados.get("Validade do Cercon", "")

        validade_cercon = st.text_input(
            "Validade do Cercon (dd/mm/aaaa)",
            value=validade_cercon_auto,
            key=f"valcercon_{prefix}"
        )

        opcoes_empresa = ["Regular", "Isento", "MEI", "Evento Temporário"]

        tipo_empresa_valor = dados.get("Tipo de Empresa", opcoes_empresa[0])
        if tipo_empresa_valor in opcoes_empresa:
            tipo_empresa_index = opcoes_empresa.index(tipo_empresa_valor)
        else:
            tipo_empresa_index = 0

        tipo_empresa = st.selectbox(
            "Tipo de Empresa",
            opcoes_empresa,
            index=tipo_empresa_index,
            key=f"empresa_{prefix}"
        )


        contato = st.text_input("Contato", value=dados["Contato"], key=f"cont_{prefix}")

        opcoes_militar = [
            "Asp Of D'Lauan",
            "2° Sgt Tamilla",
            "2° Sgt Ribeiro",
            "2° Sgt Éderson"
        ]

        militar_valor = dados.get("Militar Responsável", opcoes_militar[0])
        if militar_valor in opcoes_militar:
            militar_index = opcoes_militar.index(militar_valor)
        else:
            militar_index = 0

        militar = st.selectbox(
            "Militar Responsável",
            opcoes_militar,
            index=militar_index,
            key=f"mil_{prefix}"
        )


        opcoes_andamento = [
            "Protocolado",
            "Vistoria Feita",
            "Cercon Impresso",
            "Empresa Encerrou",
            "Empresa/Proprietário Não Localizado"
        ]


        andamento_valor = dados.get("Andamento", opcoes_andamento[0])
        if andamento_valor in opcoes_andamento:
            andamento_index = opcoes_andamento.index(andamento_valor)
        else:
            andamento_index = 0

        andamento = st.selectbox(
            "Andamento",
            opcoes_andamento,
            index=andamento_index,
            key=f"and_{prefix}"
        )


        opcoes_cidade = [
            "Porangatu",
            "Santa Tereza",
            "Estrela do Norte",
            "Formoso",
            "Trombas",
            "Novo Planalto",
            "Montividiu",
            "Mutunópolis"
        ]

        cidade_valor = dados.get("Cidade", opcoes_cidade[0])
        if cidade_valor in opcoes_cidade:
            cidade_index = opcoes_cidade.index(cidade_valor)
        else:
            cidade_index = 0

        cidade = st.selectbox(
            "Cidade",
            opcoes_cidade,
            index=cidade_index,
            key=f"cid_{prefix}"
        )



    return {
    "Data de Protocolo": data_raw,
    "Nº de Protocolo": protocolo,
    "Tipo de Serviço": tipo,
    "CPF/CNPJ": cpf,
    "Nome Fantasia": nome,
    "Área (m²)": area,
    "Notificação": notificacao,
    "Validade do Boleto": validade_boleto,
    "Validade do Cercon": validade_cercon,
    "Tipo de Empresa": tipo_empresa,
    "Contato": contato,
    "Militar Responsável": militar,
    "Andamento": andamento,
    "Cidade": cidade
}



# -----------------------------------------------------------
#                     APLICATIVO PRINCIPAL
# -----------------------------------------------------------

def app(TABELA):
    st.title(f"📂 Gerenciamento de Protocolos — {TABELA}")

    # Carrega todos os dados da tabela
    df_all = carregar_dados(TABELA)

    # Busca geral (aplica só na aba "Protocolos Encontrados")
    termo = st.text_input("🔎 Buscar protocolo (por nome, CPF, militar, tipo...)")
    df = df_all.copy()
    if termo:
        termo_low = termo.lower()
        df = df[df.apply(lambda r: termo_low in str(r.values).lower(), axis=1)]

    # ----------------- CADASTRAR NOVO PROTOCOLO -----------------
    with st.expander("➕ Cadastrar Novo Protocolo", expanded=False):
        dados_novos = formulario_protocolo(prefix="novo")

        if st.button("💾 Salvar Novo Protocolo", key="salvar_novo"):
            try:
                data_protocolo = datetime.strptime(dados_novos["Data de Protocolo"], "%d/%m/%Y").date()
                validade_boleto = datetime.strptime(dados_novos["Validade do Boleto"], "%d/%m/%Y").date()
                validade_cercon = datetime.strptime(dados_novos["Validade do Cercon"], "%d/%m/%Y").date()
            except ValueError:
                st.error("❌ Uma das datas está em formato inválido. Use dd/mm/aaaa.")
                st.stop()

            novo = {
                "ID": cria_id(),
                "Data de Protocolo": data_protocolo.strftime("%d/%m/%Y"),
                "Nº de Protocolo": dados_novos["Nº de Protocolo"],
                "Tipo de Serviço": dados_novos["Tipo de Serviço"],
                "CPF/CNPJ": dados_novos["CPF/CNPJ"],
                "Nome Fantasia": dados_novos["Nome Fantasia"],
                "Área (m²)": dados_novos["Área (m²)"],
                "Notificação": dados_novos["Notificação"],
                "Validade do Boleto": validade_boleto.strftime("%d/%m/%Y"),
                "Validade do Cercon": validade_cercon.strftime("%d/%m/%Y"),
                "Tipo de Empresa": dados_novos["Tipo de Empresa"],
                "Contato": dados_novos["Contato"],
                "Militar Responsável": dados_novos["Militar Responsável"],
                "Andamento": dados_novos["Andamento"],
                "Cidade": dados_novos["Cidade"]

            }
            insert(TABELA, novo)
            st.success("✅ Novo protocolo salvo com sucesso!")
            st.rerun()

    st.divider()
    st.subheader(f"📋 Protocolos Encontrados: {len(df)}")

    # -----------------------------------------------------------
    #       PREPARO DOS DATAFRAMES PARA FILTROS DE CERCON
    # -----------------------------------------------------------
    # -----------------------------------------------------------
#       PREPARO DOS DATAFRAMES PARA FILTROS E NOVOS HOJE
# -----------------------------------------------------------

    df_temp = df_all.copy()

    # Conversão segura das datas
    df_temp["Validade_dt"] = pd.to_datetime(
        df_temp["Validade do Cercon"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df_temp["Boleto_dt"] = pd.to_datetime(
        df_temp["Validade do Boleto"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df_temp["DataProt_dt"] = pd.to_datetime(
        df_temp["Data de Protocolo"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    hoje = date.today()
    limite_proximo = hoje + timedelta(days=30)
    limite_vencidos = hoje - timedelta(days=365)


    # -----------------------------------------------------------
    #                      ABAS DE VISUALIZAÇÃO
    # -----------------------------------------------------------

    # -----------------------------------------------------------
#     BADGES DINÂMICOS NAS ABAS (minimalistas e atualizados)
# -----------------------------------------------------------

    df_alert = df_all.copy()
    df_alert["Validade_dt"] = pd.to_datetime(df_alert["Validade do Cercon"], format="%d/%m/%Y", errors="coerce")
    df_alert["Boleto_dt"] = pd.to_datetime(df_alert["Validade do Boleto"], format="%d/%m/%Y", errors="coerce")
    df_alert["DataProt_dt"] = pd.to_datetime(df_alert["Data de Protocolo"],format="%d/%m/%Y",dayfirst=True,errors="coerce") 
    
    # --- Cálculos ---
    qtd_novos = df_alert[df_alert["DataProt_dt"].dt.date == hoje].shape[0]

    qtd_proximos = df_alert[
        (df_alert["Validade_dt"] >= pd.Timestamp(hoje)) &
        (df_alert["Validade_dt"] <= pd.Timestamp(limite_proximo))
    ].shape[0]

    qtd_vencidos = df_alert[
        (df_alert["Validade_dt"] < pd.Timestamp(hoje)) &
        (df_alert["Validade_dt"] >= pd.Timestamp(limite_vencidos))
    ].shape[0]

    qtd_expirados = df_alert[
    (
        (df_alert["Boleto_dt"] < pd.Timestamp(hoje)) &
        (df_alert["Andamento"] != "Cercon Impresso")
    ) | (
        (df_alert["Boleto_dt"] + pd.Timedelta(days=120) < pd.Timestamp(hoje)) &
        (df_alert["Andamento"] != "Cercon Impresso")
    )
    ].shape[0]



    # --- Construção dos badges ---
    ABA1 = "📋 Protocolos Encontrados"
    ABA2 = f"🟨 Cercons Próximos ({qtd_proximos})" if qtd_proximos > 0 else "🟨 Cercons Próximos (0)"
    ABA3 = f"🟥 Cercons Vencidos ({qtd_vencidos})" if qtd_vencidos > 0 else "🟥 Cercons Vencidos (0)"
    ABA4 = f"⚠️ Expirados ({qtd_expirados})" if qtd_expirados > 0 else "⚠️ Expirados (0)"
    ABA5 = f"🆕 Novos Hoje ({qtd_novos})" if qtd_novos > 0 else "🆕 Novos Hoje (0)"

    # --- Cria as abas com badges ---
    # --- Cria as abas com badges ---
    aba_princ, aba_prox, aba_venc, aba_exp, aba_novos = st.tabs([
        ABA1, ABA2, ABA3, ABA4, ABA5
    ])



    # ---------------------------
    # 1️⃣ ABA: PROTOCOLOS ENCONTRADOS
    # ---------------------------
    with aba_princ:
        if df.empty:
            st.info("Nenhum protocolo encontrado.")
        else:
            for _, row in df.iterrows():
                with st.expander(f"🧾 {row['Nº de Protocolo']} — {row['Nome Fantasia']}"):
                    dados = formulario_protocolo(row, prefix=row["ID"])

                    # Controle da confirmação de exclusão
                    confirma_key = f"confirma_exclusao_{row['ID']}"
                    if confirma_key not in st.session_state:
                        st.session_state[confirma_key] = False

                    # Formulário de ações (atualizar / excluir)
                    with st.form(key=f"form_acoes_{row['ID']}"):
                        col1, col2 = st.columns(2)
                        atualizar = col1.form_submit_button("💾 Atualizar")
                        excluir = col2.form_submit_button("🗑️ Excluir")

                        if atualizar:
                            try:
                                datetime.strptime(dados["Data de Protocolo"], "%d/%m/%Y")
                                datetime.strptime(dados["Validade do Boleto"], "%d/%m/%Y")
                                datetime.strptime(dados["Validade do Cercon"], "%d/%m/%Y")
                            except ValueError:
                                st.error("❌ Uma das datas está em formato inválido. Use dd/mm/aaaa.")
                                st.stop()

                            update(
                                TABELA,
                                list(dados.keys()),
                                list(dados.values()),
                                where=f"ID,eq,{row['ID']}",
                                tipos_colunas=TIPOS_COLUNAS
                            )
                            st.success("✅ Protocolo atualizado com sucesso!")
                            st.rerun()

                        if excluir:
                            st.session_state[confirma_key] = True

                    # Confirmação de exclusão FORA do form
                    if st.session_state.get(confirma_key, False):
                        st.warning(f"❗ Tem certeza que deseja excluir o protocolo {row['Nº de Protocolo']}?")
                        col_c1, col_c2 = st.columns(2)
                        confirma = col_c1.button("🚨 Confirmar Exclusão", key=f"confirma_{row['ID']}")
                        cancela = col_c2.button("Cancelar", key=f"cancela_{row['ID']}")

                        if confirma:
                            delete(TABELA, where=f"ID,eq,{row['ID']}", tipos_colunas=TIPOS_COLUNAS)
                            st.success("🗑️ Protocolo excluído com sucesso!")
                            st.session_state[confirma_key] = False
                            st.rerun()
                        elif cancela:
                            st.info("✅ Exclusão cancelada.")
                            st.session_state[confirma_key] = False

    # ---------------------------
    # 2️⃣ ABA: CERCONS PRÓXIMOS AO VENCIMENTO (≤ 30 DIAS)
    # ---------------------------
    # ---------------------------
# 2️⃣ ABA: CERCONS PRÓXIMOS AO VENCIMENTO (≤ 30 DIAS)
# ---------------------------
    with aba_prox:
        st.markdown("### 🟨 Cercons Próximos ao Vencimento (≤ 30 dias)")

        df_proximos = df_temp[
            (df_temp["Validade_dt"] >= pd.Timestamp(hoje)) &
            (df_temp["Validade_dt"] <= pd.Timestamp(limite_proximo))
        ].sort_values("Validade_dt")

        if df_proximos.empty:
            st.info("Nenhum Cercon próximo ao vencimento nos próximos 30 dias.")
        else:
            for _, row in df_proximos.iterrows():

                with st.expander(f"🟨 {row['Nº de Protocolo']} — {row['Nome Fantasia']}", expanded=False):

                    dados = formulario_protocolo(row, prefix=f"prox_{row['ID']}")

                    # Controle da confirmação de exclusão
                    confirma_key = f"confirma_exclusao_prox_{row['ID']}"
                    if confirma_key not in st.session_state:
                        st.session_state[confirma_key] = False

                    # Formulário de ações
                    with st.form(key=f"form_prox_{row['ID']}"):
                        col1, col2 = st.columns(2)
                        atualizar = col1.form_submit_button("💾 Atualizar")
                        excluir = col2.form_submit_button("🗑️ Excluir")

                        if atualizar:
                            update(
                                TABELA,
                                list(dados.keys()),
                                list(dados.values()),
                                where=f"ID,eq,{row['ID']}",
                                tipos_colunas=TIPOS_COLUNAS
                            )
                            st.success("Atualizado!")
                            st.rerun()

                        if excluir:
                            st.session_state[confirma_key] = True

                    # Confirmação
                    if st.session_state.get(confirma_key, False):
                        st.warning("Confirma exclusão?")
                        col_c1, col_c2 = st.columns(2)

                        confirma = col_c1.button("🚨 Confirmar Exclusão", key=f"del_prox_{row['ID']}")
                        cancela = col_c2.button("Cancelar", key=f"cancela_prox_{row['ID']}")
                        
                        if confirma:
                            delete(TABELA, where=f"ID,eq,{row['ID']}", tipos_colunas=TIPOS_COLUNAS)
                            st.success("Excluído!")
                            st.rerun()
                        elif cancela:
                            st.session_state[confirma_key] = False


    
    # ---------------------------
# 3️⃣ ABA: CERCONS VENCIDOS (< 365 DIAS)
# ---------------------------
    with aba_venc:
        st.markdown("### 🟥 Cercons Vencidos (últimos 365 dias)")

        df_vencidos = df_temp[
            (df_temp["Validade_dt"] < pd.Timestamp(hoje)) &
            (df_temp["Validade_dt"] >= pd.Timestamp(limite_vencidos))
        ].sort_values("Validade_dt")

        if df_vencidos.empty:
            st.success("Nenhum Cercon vencido nos últimos 365 dias! 🎉")
        else:
            for _, row in df_vencidos.iterrows():

                dias_vencidos = (hoje - row["Validade_dt"].date()).days if pd.notna(row["Validade_dt"]) else "N/A"

                with st.expander(f"🟥 {row['Nº de Protocolo']} — {row['Nome Fantasia']} ({dias_vencidos} dias vencido)", expanded=False):

                    dados = formulario_protocolo(row, prefix=f"venc_{row['ID']}")

                    confirma_key = f"confirma_exclusao_venc_{row['ID']}"
                    if confirma_key not in st.session_state:
                        st.session_state[confirma_key] = False

                    with st.form(key=f"form_venc_{row['ID']}"):
                        col1, col2 = st.columns(2)
                        atualizar = col1.form_submit_button("💾 Atualizar")
                        excluir = col2.form_submit_button("🗑️ Excluir")

                        if atualizar:
                            update(
                                TABELA,
                                list(dados.keys()),
                                list(dados.values()),
                                where=f"ID,eq,{row['ID']}",
                                tipos_colunas=TIPOS_COLUNAS
                            )
                            st.success("Atualizado!")
                            st.rerun()

                        if excluir:
                            st.session_state[confirma_key] = True

                    if st.session_state.get(confirma_key, False):
                        st.warning("Confirma exclusão?")
                        col_c1, col_c2 = st.columns(2)

                        confirma = col_c1.button("🚨 Confirmar Exclusão", key=f"del_venc_{row['ID']}")
                        cancela = col_c2.button("Cancelar", key=f"cancela_venc_{row['ID']}")

                        if confirma:
                            delete(TABELA, where=f"ID,eq,{row['ID']}", tipos_colunas=TIPOS_COLUNAS)
                            st.success("Excluído!")
                            st.rerun()
                        elif cancela:
                            st.session_state[confirma_key] = False


   
    # ---------------------------
# 4️⃣ ABA: PROCESSOS EXPIRADOS
# ---------------------------
    with aba_exp:
        st.markdown("### ⚠️ Processos Expirados")

        # 🔹 Critério 1: Boleto vencido e andamento ≠ Cercon Impresso
        boleto_vencido = (
            (df_temp["Boleto_dt"] < pd.Timestamp(hoje)) &
            (df_temp["Andamento"] != "Cercon Impresso")
        )

        # 🔹 Critério 2: Inatividade
        # (120 dias após vencimento do boleto e andamento ≠ Cercon Impresso)
        inatividade = (
            (df_temp["Boleto_dt"] + pd.Timedelta(days=120) < pd.Timestamp(hoje)) &
            (df_temp["Andamento"] != "Cercon Impresso")
        )

        df_expirados = df_temp[
            boleto_vencido | inatividade
        ].sort_values("DataProt_dt", ascending=False)

        if df_expirados.empty:
            st.info("Nenhum processo expirado.")
        else:
            for _, row in df_expirados.iterrows():

                # 🔹 Definição do motivo
                if (
                    row["Boleto_dt"] + pd.Timedelta(days=120) < pd.Timestamp(hoje)
                    and row["Andamento"] != "Cercon Impresso"
                ):
                    motivo = "Inatividade (> 120 dias após vencimento do boleto)"
                else:
                    motivo = "Boleto Vencido"

                with st.expander(
                    f"⚠️ {row['Nº de Protocolo']} — {row['Nome Fantasia']} ({motivo})",
                    expanded=False
                ):
                    dados = formulario_protocolo(row, prefix=f"exp_{row['ID']}")

                    confirma_key = f"confirma_exclusao_exp_{row['ID']}"
                    if confirma_key not in st.session_state:
                        st.session_state[confirma_key] = False

                    with st.form(key=f"form_exp_{row['ID']}"):
                        col1, col2 = st.columns(2)
                        atualizar = col1.form_submit_button("💾 Atualizar")
                        excluir = col2.form_submit_button("🗑️ Excluir")

                        if atualizar:
                            update(
                                TABELA,
                                list(dados.keys()),
                                list(dados.values()),
                                where=f"ID,eq,{row['ID']}",
                                tipos_colunas=TIPOS_COLUNAS
                            )
                            st.success("Atualizado!")
                            st.rerun()

                        if excluir:
                            st.session_state[confirma_key] = True

                    # 🔹 Confirmação de exclusão
                    if st.session_state.get(confirma_key, False):
                        st.warning("Deseja excluir este protocolo?")
                        col_c1, col_c2 = st.columns(2)

                        confirma = col_c1.button(
                            "🚨 Confirmar Exclusão",
                            key=f"del_exp_{row['ID']}"
                        )
                        cancela = col_c2.button(
                            "Cancelar",
                            key=f"cancela_exp_{row['ID']}"
                        )

                        if confirma:
                            delete(
                                TABELA,
                                where=f"ID,eq,{row['ID']}",
                                tipos_colunas=TIPOS_COLUNAS
                            )
                            st.success("Excluído!")
                            st.rerun()
                        elif cancela:
                            st.session_state[confirma_key] = False



    # ---------------------------
# 5️⃣ ABA: NOVOS PROTOCOLOS CADASTRADOS HOJE
# ---------------------------
    with aba_novos:
            st.markdown("### 🆕 Novos Protocolos Cadastrados Hoje")

            df_novos = df_temp[
                (df_temp["DataProt_dt"] == pd.Timestamp(hoje))
            ].sort_values("DataProt_dt", ascending=False)

            if df_novos.empty:
                st.info("Nenhum protocolo foi cadastrado hoje.")
            else:
                for _, row in df_novos.iterrows():

                    with st.expander(f"🆕 {row['Nº de Protocolo']} — {row['Nome Fantasia']}", expanded=False):

                        # formulário
                        dados = formulario_protocolo(row, prefix=f"novo_{row['ID']}")

                        # chave de confirmação
                        confirma_key = f"confirma_exclusao_novos_{row['ID']}"
                        if confirma_key not in st.session_state:
                            st.session_state[confirma_key] = False

                        # Formulário de ações
                        with st.form(key=f"form_novos_{row['ID']}"):
                            col1, col2 = st.columns(2)
                            atualizar = col1.form_submit_button("💾 Atualizar")
                            excluir = col2.form_submit_button("🗑️ Excluir")

                            if atualizar:
                                update(
                                    TABELA,
                                    list(dados.keys()),
                                    list(dados.values()),
                                    where=f"ID,eq,{row['ID']}",
                                    tipos_colunas=TIPOS_COLUNAS
                                )
                                st.success("Atualizado!")
                                st.rerun()

                            if excluir:
                                st.session_state[confirma_key] = True

                        # CONFIRMAÇÃO
                        if st.session_state.get(confirma_key, False):
                            st.warning("Deseja realmente excluir este protocolo?")
                            col_c1, col_c2 = st.columns(2)

                            confirma = col_c1.button("🚨 Confirmar Exclusão", key=f"del_novos_{row['ID']}")
                            cancela = col_c2.button("Cancelar", key=f"cancela_novos_{row['ID']}")

                            if confirma:
                                delete(TABELA, where=f"ID,eq,{row['ID']}", tipos_colunas=TIPOS_COLUNAS)
                                st.success("Excluído!")
                                st.rerun()
                            elif cancela:
                                st.session_state[confirma_key] = False



