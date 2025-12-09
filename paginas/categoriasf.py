# -*- coding: utf-8 -*-
# /paginas/categorias.py
# Autor: Yuri D’LAUAN
# Integração direta com Google Sheets via conversa_banco.py

import streamlit as st
import pandas as pd
from funcoes_compartilhadas.conversa_banco import select, insert, update, delete
from funcoes_compartilhadas.cria_id import cria_id  # Gera IDs únicos
import math
from datetime import date

# ───────────────────────────────────────────────────────────────
# 🔢 Configuração da tabela e tipos de colunas
# ───────────────────────────────────────────────────────────────
TABELA = "categorias"

TIPOS_COLUNAS = {
    "ID": "id",
    "Nº de Protocolo": "texto",
    "Tipo de Serviço": "texto",
    "CPF/CNPJ": "texto",
    "Nome Fantasia": "texto",
    "Área (m²)": "numero",
    "Valor Total": "numero100",
    "Validade do Cercon": "data",
    "Prazo de Vistoria": "data",
    "Contato": "texto",
    "Militar Responsável": "texto",
    "Andamento": "texto"
}

# ───────────────────────────────────────────────────────────────
# 🔧 Funções auxiliares
# ───────────────────────────────────────────────────────────────
def sanitize_number(value, default=0.0):
    """Converte valores em float de forma segura."""
    try:
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        value = float(value)
        if math.isnan(value):
            return default
        return value
    except (ValueError, TypeError):
        return default


def carregar_dados():
    df = select(TABELA, TIPOS_COLUNAS)
    return pd.DataFrame(df)


# ───────────────────────────────────────────────────────────────
# 🚀 Interface principal
# ───────────────────────────────────────────────────────────────
def app():
    st.title("📂 Gerenciamento de Protocolos - CBMGO")

    # Carregar dados
    df = carregar_dados()

    # Campo de busca
    termo = st.text_input("🔎 Buscar protocolo (por nome, CPF, militar, tipo...)")
    if termo:
        termo = termo.lower()
        df = df[df.apply(lambda r: termo in str(r.values).lower(), axis=1)]

    # ─────────────── Cadastro de novo protocolo ────────────────
    with st.expander("➕ Cadastrar Novo Protocolo", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            protocolo = st.text_input("Nº de Protocolo")
            tipo = st.selectbox("Tipo de Serviço", [
                "Vistoria para Funcionamento",
                "Licenciamento Facilitado",
                "Análise de Projeto",
                "Substituição de Projeto"
            ])
            cpf = st.text_input("CPF/CNPJ")
            nome = st.text_input("Nome Fantasia")
            area = sanitize_number(st.text_input("Área (m²)", "0"))
            valor = sanitize_number(st.text_input("Valor Total (R$)", "0"))
        with col2:
            validade = st.date_input("Validade do Cercon", date.today())
            prazo = st.date_input("Prazo de Vistoria", date.today())
            contato = st.text_input("Contato")
            militar = st.text_input("Militar Responsável")
            andamento = st.selectbox("Andamento", [
                "Boleto Impresso", "Boleto Entregue", "Boleto Pago",
                "Isento", "MEI", "Processo Expirado", "Empresa Encerrou"
            ])

        if st.button("💾 Salvar Novo Protocolo"):
            novo = {
                "ID": cria_id(),
                "Nº de Protocolo": protocolo,
                "Tipo de Serviço": tipo,
                "CPF/CNPJ": cpf,
                "Nome Fantasia": nome,
                "Área (m²)": area,
                "Valor Total": valor,
                "Validade do Cercon": str(validade),
                "Prazo de Vistoria": str(prazo),
                "Contato": contato,
                "Militar Responsável": militar,
                "Andamento": andamento
            }
            insert(TABELA, novo)
            st.success("✅ Novo protocolo salvo com sucesso!")

    # ─────────────── Exibição e edição dos registros ────────────────
    st.divider()
    st.subheader(f"📋 Protocolos Encontrados: {len(df)}")

    if df.empty:
        st.info("Nenhum protocolo encontrado.")
    else:
        for _, row in df.iterrows():
            uid = row["ID"]
            with st.expander(f"🧾 {row['Nº de Protocolo']} - {row['Nome Fantasia']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome Fantasia", value=row["Nome Fantasia"], key=f"nome_{uid}")
                    cpf = st.text_input("CPF/CNPJ", value=row["CPF/CNPJ"], key=f"cpf_{uid}")
                    tipo = st.selectbox("Tipo de Serviço", [
                        "Vistoria para Funcionamento",
                        "Licenciamento Facilitado",
                        "Análise de Projeto",
                        "Substituição de Projeto"
                    ], index=0, key=f"tipo_{uid}")
                    area = st.number_input("Área (m²)", min_value=0.0, format="%.2f",
                                           value=sanitize_number(row["Área (m²)"]), key=f"area_{uid}")
                    valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f",
                                            value=sanitize_number(row["Valor Total"]), key=f"valor_{uid}")
                with col2:
                    validade = st.text_input("Validade do Cercon", value=row.get("Validade do Cercon", ""), key=f"val_{uid}")
                    prazo = st.text_input("Prazo de Vistoria", value=row.get("Prazo de Vistoria", ""), key=f"prazo_{uid}")
                    contato = st.text_input("Contato", value=row.get("Contato", ""), key=f"cont_{uid}")
                    militar = st.text_input("Militar Responsável", value=row.get("Militar Responsável", ""), key=f"mil_{uid}")
                    andamento = st.selectbox("Andamento", [
                        "Boleto Impresso", "Boleto Entregue", "Boleto Pago",
                        "Isento", "MEI", "Processo Expirado", "Empresa Encerrou"
                    ], index=0, key=f"and_{uid}")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("💾 Salvar Alterações", key=f"save_{uid}"):
                        campos = [
                            "Nome Fantasia", "CPF/CNPJ", "Tipo de Serviço", "Área (m²)",
                            "Valor Total", "Validade do Cercon", "Prazo de Vistoria",
                            "Contato", "Militar Responsável", "Andamento"
                        ]
                        valores = [
                            nome, cpf, tipo, area, valor, validade,
                            prazo, contato, militar, andamento
                        ]
                        update(TABELA, campos, valores, f"ID,=,{uid}", TIPOS_COLUNAS)
                        st.success("✅ Protocolo atualizado!")

                with col2:
                    if st.button("🗑️ Excluir Protocolo", key=f"del_{uid}"):
                        delete(TABELA, f"ID,=,{uid}", TIPOS_COLUNAS)
                        st.warning("🗑️ Protocolo excluído com sucesso!")

    st.markdown("---")
    st.caption("Sistema integrado ao Google Sheets via camada conversa_banco.py")


# Execução local
if __name__ == "__main__":
    app()
