# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import math
from funcoes_compartilhadas.conversa_banco import select, insert, update, delete
from funcoes_compartilhadas.cria_id import cria_id

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES BÁSICAS
# ───────────────────────────────────────────────────────────────────────────────
TABELA = "Protocolos"

TIPOS_COLUNAS = {
    "ID": "id",
    "Data de Protocolo": "data",
    "Nº de Protocolo": "texto",
    "Tipo de Serviço": "texto",
    "CPF/CNPJ": "texto",
    "Nome Fantasia": "texto",
    "Área (m²)": "numero",
    "Valor Total": "numero100",
    "Validade do Boleto": "data",
    "Validade do Cercon": "data",
    "Prazo de Vistoria": "data",
    "Contato": "texto",
    "Militar Responsável": "texto",
    "Andamento": "texto"
}

# ───────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ───────────────────────────────────────────────────────────────────────────────
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


def calcular_vistoria(area: float) -> float:
    VALOR_BASE = 150.35
    LIMITE_AREA = 100
    VALOR_EXCEDENTE = 0.22
    if area <= LIMITE_AREA:
        return VALOR_BASE
    excedente = area - LIMITE_AREA
    return round(VALOR_BASE + excedente * VALOR_EXCEDENTE, 2)


def carregar_dados():
    df = select(TABELA, TIPOS_COLUNAS)
    df = pd.DataFrame(df)

    # Converte automaticamente qualquer valor numérico de data
    def corrige_data(valor):
        try:
            if pd.isna(valor) or str(valor).strip() == "":
                return ""
            if str(valor).isdigit():
                # Trata o formato numérico (ex: 45973)
                data = pd.to_datetime("1899-12-30") + pd.to_timedelta(int(valor), unit="D")
                return data.strftime("%d/%m/%Y")
            else:
                # Tenta converter de string
                data = pd.to_datetime(str(valor), dayfirst=True, errors="coerce")
                if pd.notna(data):
                    return data.strftime("%d/%m/%Y")
                return str(valor)
        except Exception:
            return str(valor)

    for coluna in ["Data de Protocolo", "Validade do Boleto", "Validade do Cercon", "Prazo de Vistoria"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(corrige_data)

    return df



# ───────────────────────────────────────────────────────────────────────────────
# FORMULÁRIO PADRÃO USADO EM CADASTRO E EDIÇÃO
# ───────────────────────────────────────────────────────────────────────────────
def formulario_protocolo(dados=None, prefix=""):
    if dados is None:
        data_protocolo_padrao = date.today()
        dados = {
            "Data de Protocolo": data_protocolo_padrao.strftime("%d/%m/%Y"),
            "Nº de Protocolo": "",
            "Tipo de Serviço": "",
            "CPF/CNPJ": "",
            "Nome Fantasia": "",
            "Área (m²)": 0.0,
            "Valor Total": 0.0,
            "Validade do Boleto": "",
            "Validade do Cercon": "",
            "Prazo de Vistoria": "",
            "Contato": "",
            "Militar Responsável": "",
            "Andamento": ""
        }

    col1, col2 = st.columns(2)

    with col1:
        data_raw = st.text_input("Data de Protocolo (dd/mm/aaaa)",
                                 value=dados["Data de Protocolo"], key=f"data_{prefix}")

        try:
            data_convertida = datetime.strptime(data_raw, "%d/%m/%Y").date()
        except ValueError:
            data_convertida = date.today()

        protocolo = st.text_input("Nº de Protocolo",
                                  value=dados["Nº de Protocolo"], key=f"prot_{prefix}")
        tipo = st.selectbox("Tipo de Serviço",
                            ["Vistoria para Funcionamento", "Licenciamento Facilitado",
                             "Análise de Projeto", "Substituição de Projeto"],
                            index=0, key=f"tipo_{prefix}")
        cpf = st.text_input("CPF/CNPJ", value=dados["CPF/CNPJ"], key=f"cpf_{prefix}")
        nome = st.text_input("Nome Fantasia", value=dados["Nome Fantasia"], key=f"nome_{prefix}")

        area = st.number_input("Área (m²)", min_value=0.0, format="%.2f",
                               value=float(dados.get("Área (m²)", 0.0)), key=f"area_{prefix}")

        VALOR_BASE = 150.35
        LIMITE_AREA = 100
        VALOR_EXCEDENTE = 0.22
        if area <= LIMITE_AREA:
            valor_calculado = VALOR_BASE
        else:
            excedente = area - LIMITE_AREA
            valor_calculado = round(VALOR_BASE + excedente * VALOR_EXCEDENTE, 2)

        valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f",
                                value=valor_calculado if prefix == "novo" else float(dados.get("Valor Total", 0.0)),
                                key=f"valor_{prefix}")

        st.caption(f"💡 Valor calculado automaticamente: R$ {valor_calculado:.2f}")

    with col2:
        validade_boleto = st.text_input("Validade do Boleto (dd/mm/aaaa)",
                                        value=(data_convertida + timedelta(days=30)).strftime("%d/%m/%Y"),
                                        key=f"valboleto_{prefix}")
        validade_cercon = st.text_input("Validade do Cercon (dd/mm/aaaa)",
                                        value=(data_convertida + timedelta(days=365)).strftime("%d/%m/%Y"),
                                        key=f"valcercon_{prefix}")
        prazo_vistoria = st.text_input(" Vistoria até: (dd/mm/aaaa)",
                                       value=(data_convertida + timedelta(days=30)).strftime("%d/%m/%Y"),
                                       key=f"vistoria_{prefix}")
        contato = st.text_input("Contato", value=dados["Contato"], key=f"cont_{prefix}")
        militar = st.selectbox("Militar Responsável",
                               ["Asp Of D'Lauan", "2° Sgt Tamilla", "2° Sgt Ribeiro", "2° Sgt Éderson"],
                               index=0, key=f"mil_{prefix}")
        andamento = st.selectbox("Andamento",
                                 ["Boleto Impresso", "Boleto Entregue", "Boleto Pago",
                                  "Isento", "MEI", "Processo Expirado", "Empresa Encerrou",
                                  "Cercon Impresso", "Empresa Não Encontrada"],
                                 index=0, key=f"and_{prefix}")

    return {
        "Data de Protocolo": data_raw,
        "Nº de Protocolo": protocolo,
        "Tipo de Serviço": tipo,
        "CPF/CNPJ": cpf,
        "Nome Fantasia": nome,
        "Área (m²)": area,
        "Valor Total": valor,
        "Validade do Boleto": validade_boleto,
        "Validade do Cercon": validade_cercon,
        "Prazo de Vistoria": prazo_vistoria,
        "Contato": contato,
        "Militar Responsável": militar,
        "Andamento": andamento
    }


# ───────────────────────────────────────────────────────────────────────────────
# INTERFACE PRINCIPAL
# ───────────────────────────────────────────────────────────────────────────────
def app():

    if st.session_state.get("forcar_reload"):
        st.session_state.pop("forcar_reload")
        st.rerun()

    st.title("📂 Gerenciamento de Protocolos - PORANGATU")

    # Força o idioma do navegador para PT-BR
    st.markdown("""
        <script>
        const lang = document.documentElement.lang;
        if (!lang || lang !== "pt-BR") {
            document.documentElement.lang = "pt-BR";
        }
        </script>
    """, unsafe_allow_html=True)

    df = carregar_dados()

    # 🔄 Mescla registros recém-inseridos que ainda não apareceram no backend
    buf = st.session_state.get("__buffer_inseridos__", [])
    if buf:
        ids_exist = set(df["ID"].astype(str)) if not df.empty else set()
        pendentes = [r for r in buf if str(r["ID"]) not in ids_exist]
        if pendentes:
            df = pd.concat([df, pd.DataFrame(pendentes)], ignore_index=True)

        # 🔄 Mescla registros recém-inseridos que ainda não apareceram no backend
    
    # ───────────────────────────────────────────────────────────────
    # 1️⃣ CADASTRAR NOVO PROTOCOLO
    # ───────────────────────────────────────────────────────────────
        # ───────────────────────────────────────────────────────────────
    # 1️⃣ CADASTRAR NOVO PROTOCOLO
    # ───────────────────────────────────────────────────────────────
    with st.expander("➕ Cadastrar Novo Protocolo", expanded=False):
        dados_novos = formulario_protocolo(prefix="novo")

        if st.button("💾 Salvar Novo Protocolo", key="salva_protocolo"):
            try:
                data_protocolo = datetime.strptime(dados_novos["Data de Protocolo"], "%d/%m/%Y").date()
                validade_boleto = datetime.strptime(dados_novos["Validade do Boleto"], "%d/%m/%Y").date()
                validade_cercon = datetime.strptime(dados_novos["Validade do Cercon"], "%d/%m/%Y").date()
                prazo_vistoria = datetime.strptime(dados_novos["Prazo de Vistoria"], "%d/%m/%Y").date()
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
                "Valor Total": dados_novos["Valor Total"],
                "Validade do Boleto": validade_boleto.strftime("%d/%m/%Y"),
                "Validade do Cercon": validade_cercon.strftime("%d/%m/%Y"),
                "Prazo de Vistoria": prazo_vistoria.strftime("%d/%m/%Y"),
                "Contato": dados_novos["Contato"],
                "Militar Responsável": dados_novos["Militar Responsável"],
                "Andamento": dados_novos["Andamento"]
            }

            # 1) Grava no banco
            insert(TABELA, novo)

            # 2) Guarda no buffer local para aparecer imediatamente (mesmo sem o backend)
            st.session_state.setdefault("__buffer_inseridos__", []).append(novo)

            # 3) Atualiza imediatamente a visão usando um df_local (df atual + novo)
            df_local = df.copy() if 'df' in locals() else pd.DataFrame()
            df_local = pd.concat([df_local, pd.DataFrame([novo])], ignore_index=True)

            # 4) Recalcula as listas com base nesse df_local (sem depender do backend)
            df_local["Validade do Cercon_dt"] = pd.to_datetime(
                df_local["Validade do Cercon"], dayfirst=True, errors="coerce"
            )
            hoje = pd.Timestamp.today().normalize()
            limite = hoje + pd.Timedelta(days=30)
            proximos_vencer = df_local[
                (df_local["Validade do Cercon_dt"] >= hoje) &
                (df_local["Validade do Cercon_dt"] <= limite)
            ]
            vencidos = df_local[df_local["Validade do Cercon_dt"] < hoje]

            # 5) Feedback e rerun padrão
            st.success("✅ Protocolo salvo e já considerado nas listas!")
            st.rerun()

    # ───────────────────────────────────────────────────────────────
    # 2️⃣ PROTOCOLOS EXISTENTES
    # ───────────────────────────────────────────────────────────────
    st.divider()
    st.subheader(f"📋 Protocolos Encontrados: {len(df)}")

    if df.empty:
        st.info("Nenhum protocolo encontrado.")
    else:
        # ─── TRATAMENTO E CLASSIFICAÇÃO DE VENCIMENTOS ──────────────────────────────
        def para_data(valor):
            try:
                if pd.isna(valor) or str(valor).strip() == "":
                    return pd.NaT
                return pd.to_datetime(str(valor).strip(), dayfirst=True, errors="coerce")
            except Exception:
                return pd.NaT

        # Converte "Validade do Cercon" para datetime (nova coluna auxiliar)
        df["Validade do Cercon_dt"] = df["Validade do Cercon"].apply(para_data)

        hoje = pd.Timestamp.today().normalize()
        limite = hoje + pd.Timedelta(days=30)

        # Identifica protocolos próximos do vencimento (nos próximos 30 dias)
        proximos_vencer = df[
            (df["Validade do Cercon_dt"] >= hoje) &
            (df["Validade do Cercon_dt"] <= limite)
        ]

        # Identifica protocolos vencidos
        vencidos = df[df["Validade do Cercon_dt"] < hoje]

        # ─── LISTA DE PROTOCOLOS ───────────────────────────────────────────────
        for index, row in df.iterrows():
            uid = row["ID"]

            with st.expander(f"🧾 {row['Nº de Protocolo']} - {row['Nome Fantasia']}"):
                dados = formulario_protocolo(row, prefix=row["ID"])

                col1, col2 = st.columns([3, 1])

                with col1:
                    if st.button("💾 Atualizar", key=f"btn_{row['ID']}"):
                        try:
                            datetime.strptime(dados["Data de Protocolo"], "%d/%m/%Y")
                            datetime.strptime(dados["Validade do Boleto"], "%d/%m/%Y")
                            datetime.strptime(dados["Validade do Cercon"], "%d/%m/%Y")
                        except ValueError:
                            st.error("❌ Uma das datas está em formato inválido. Use dd/mm/aaaa.")
                            st.stop()

                        # 🔧 FORÇA TODAS AS DATAS A SEREM SALVAS COMO TEXTO (dd/mm/aaaa)
                        for campo in ["Data de Protocolo", "Validade do Boleto", "Validade do Cercon", "Prazo de Vistoria"]:
                            if campo in dados and dados[campo]:
                                try:
                                    data_obj = datetime.strptime(dados[campo], "%d/%m/%Y")
                                    dados[campo] = data_obj.strftime("%d/%m/%Y")
                                except Exception:
                                    pass  # ignora se já estiver correto

                        campos = list(dados.keys())
                        valores = list(dados.values())
                        where = f"ID,=,{row['ID']}"
                        update(TABELA, campos, valores, where, TIPOS_COLUNAS)

                        st.success("✅ Protocolo atualizado com sucesso!")
                        st.session_state["forcar_reload"] = True
                        st.rerun()

                with col2:
                    chave_confirma = f"confirmar_excluir_{row['ID']}"

                    if st.session_state.get(chave_confirma, False):
                        if st.button("❌ Confirmar Exclusão", key=f"confirma_{row['ID']}"):
                            delete(TABELA, f"ID,=,{row['ID']}", TIPOS_COLUNAS)
                            st.success("✅ Protocolo excluído com sucesso!")
                            st.rerun()

                        if st.button("↩️ Cancelar", key=f"cancela_{row['ID']}"):
                            st.session_state[chave_confirma] = False
                    else:
                        if st.button("🗑️ Excluir", key=f"del_{row['ID']}"):
                            st.session_state[chave_confirma] = True


        # ─── AVISOS DE VENCIMENTO ─────────────────────────────────────────────
        if not proximos_vencer.empty:
            st.divider()
            st.markdown("### ⚠️ Os seguintes Protocolos estão com Cercons próximo ao Vencimento:")
            for _, row in proximos_vencer.iterrows():
                data_formatada = (
                    row["Validade do Cercon_dt"].strftime("%d/%m/%Y")
                    if pd.notna(row["Validade do Cercon_dt"])
                    else row["Validade do Cercon"]
                )
                st.markdown(
                    f"""
                    <div style="background-color:#fff3cd;padding:10px;border-radius:6px;margin-bottom:5px">
                        <strong>{row['Nº de Protocolo']} - {row['Nome Fantasia']}</strong><br>
                        Vence em: {data_formatada}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if not vencidos.empty:
            st.divider()
            st.markdown("### ❌ Protocolos com Cercons Vencidos:")
            for _, row in vencidos.iterrows():
                data_formatada = (
                    row["Validade do Cercon_dt"].strftime("%d/%m/%Y")
                    if pd.notna(row["Validade do Cercon_dt"])
                    else row["Validade do Cercon"]
                )
                st.markdown(
                    f"""
                    <div style="background-color:#f8d7da;padding:10px;border-radius:6px;margin-bottom:5px">
                        <strong>{row['Nº de Protocolo']} - {row['Nome Fantasia']}</strong><br>
                        Vencido em: {data_formatada}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

