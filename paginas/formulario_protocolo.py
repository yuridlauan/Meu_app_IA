# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, timedelta
from .cria_id import cria_id
from .conversa_banco import insert
from .categorias_utils import sanitize_number, calcular_vistoria

def renderiza_formulario_protocolo(dados=None, prefixo="", modo="cadastro"):
    hoje = datetime.today().date()
    valores = {}

    # colunas
    col1, col2 = st.columns(2)

    with col1:
        valores["Data de Protocolo"] = st.text_input(
            "Data de Protocolo (dd/mm/aaaa)",
            value=dados.get("Data de Protocolo", hoje.strftime("%d/%m/%Y")) if dados else hoje.strftime("%d/%m/%Y"),
            key=f"data_prot_{prefixo}"
        )
        try:
            data_protocolo = datetime.strptime(valores["Data de Protocolo"], "%d/%m/%Y").date()
        except ValueError:
            st.error("Formato de data inválido. Use dd/mm/aaaa.")
            return {}, False

        valores["Nº de Protocolo"] = st.text_input("Nº de Protocolo", value=dados.get("Nº de Protocolo", "") if dados else "", key=f"numprot_{prefixo}")
        valores["Tipo de Serviço"] = st.selectbox(
            "Tipo de Serviço",
            ["Vistoria para Funcionamento", "Licenciamento Facilitado", "Análise de Projeto", "Substituição de Projeto"],
            index=0,
            key=f"tipo_{prefixo}"
        )
        valores["CPF/CNPJ"] = st.text_input("CPF/CNPJ", value=dados.get("CPF/CNPJ", "") if dados else "", key=f"cpf_{prefixo}")
        valores["Nome Fantasia"] = st.text_input("Nome Fantasia", value=dados.get("Nome Fantasia", "") if dados else "", key=f"nome_{prefixo}")
        area = sanitize_number(st.text_input("Área (m²)", value=str(dados.get("Área (m²)", "0")) if dados else "0", key=f"area_{prefixo}"))
        valores["Área (m²)"] = area
        valores["Valor Total"] = st.number_input(
            "Valor do Boleto (R$)",
            min_value=0.0,
            value=sanitize_number(dados.get("Valor Total", calcular_vistoria(area))) if dados else calcular_vistoria(area),
            format="%.2f",
            key=f"valor_{prefixo}"
        )

    with col2:
        validade_boleto_padrao = data_protocolo + timedelta(days=30)
        validade_cercon_padrao = data_protocolo + timedelta(days=365)

        valores["Validade do Boleto"] = st.text_input(
            "Validade do Boleto (dd/mm/aaaa)",
            value=dados.get("Validade do Boleto", validade_boleto_padrao.strftime("%d/%m/%Y")) if dados else validade_boleto_padrao.strftime("%d/%m/%Y"),
            key=f"valboleto_{prefixo}"
        )
        try:
            validade_boleto = datetime.strptime(valores["Validade do Boleto"], "%d/%m/%Y").date()
        except ValueError:
            st.error("❌ Validade do Boleto inválida. Use dd/mm/aaaa.")
            return {}, False

        valores["Validade do Cercon"] = st.text_input(
            "Validade do Cercon (dd/mm/aaaa)",
            value=dados.get("Validade do Cercon", validade_cercon_padrao.strftime("%d/%m/%Y")) if dados else validade_cercon_padrao.strftime("%d/%m/%Y"),
            key=f"valcercon_{prefixo}"
        )
        try:
            validade_cercon = datetime.strptime(valores["Validade do Cercon"], "%d/%m/%Y").date()
        except ValueError:
            st.error("❌ Validade do Cercon inválida. Use dd/mm/aaaa.")
            return {}, False

        if dados:
            try:
                data_protocolo = datetime.strptime(dados["Data de Protocolo"], "%d/%m/%Y").date()
            except:
                data_protocolo = hoje

        dias_passados = (hoje - data_protocolo).days
        valores["Prazo de Vistoria"] = st.number_input(
            "Prazo de Vistoria (dias restantes)",
            min_value=0,
            max_value=30,
            value=dados.get("Prazo de Vistoria", max(30 - dias_passados, 0)) if dados else max(30 - dias_passados, 0),
            key=f"prazo_{prefixo}"
        )

        valores["Contato"] = st.text_input("Contato", value=dados.get("Contato", "") if dados else "", key=f"contato_{prefixo}")
        valores["Militar Responsável"] = st.selectbox(
            "Militar Responsável",
            ["Asp Of D'Lauan", "2° Sgt Tamilla", "2° Sgt Ribeiro", "2° Sgt Éderson"],
            index=0,
            key=f"militar_{prefixo}"
        )
        valores["Andamento"] = st.selectbox(
            "Andamento",
            ["Boleto Impresso", "Boleto Entregue", "Boleto Pago", "Isento", "MEI",
             "Processo Expirado", "Empresa Encerrou", "Cercon Impresso", "Empresa Não Encontrada"],
            index=0,
            key=f"andamento_{prefixo}"
        )

    if modo == "cadastro":
        if st.button("💾 Salvar Novo Protocolo", key=f"salvar_{prefixo}"):
            novo = {
                "ID": cria_id(),
                "Data de Protocolo": valores["Data de Protocolo"],
                "Nº de Protocolo": valores["Nº de Protocolo"],
                "Tipo de Serviço": valores["Tipo de Serviço"],
                "CPF/CNPJ": valores["CPF/CNPJ"],
                "Nome Fantasia": valores["Nome Fantasia"],
                "Área (m²)": valores["Área (m²)"],
                "Valor Total": valores["Valor Total"],
                "Validade do Boleto": valores["Validade do Boleto"],
                "Validade do Cercon": valores["Validade do Cercon"],
                "Prazo de Vistoria": valores["Prazo de Vistoria"],
                "Contato": valores["Contato"],
                "Militar Responsável": valores["Militar Responsável"],
                "Andamento": valores["Andamento"]
            }
            insert("Protocolos", novo)
            st.success("✅ Novo protocolo salvo com sucesso!")
            st.rerun()

    
    if modo == "edicao":
        if st.button("💾 Salvar Alterações", key=f"update_{prefixo}"):
            from .conversa_banco import update
            campos = []
            valores_upd = []
            for k, v in valores.items():
                if str(v) != str(dados.get(k, "")):
                    campos.append(k)
                    valores_upd.append(v)
            if campos:
                update("Protocolos", campos, valores_upd, where=f"ID,eq,{dados['ID']}", tipos_colunas={
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
                    "Prazo de Vistoria": "numero",
                    "Contato": "texto",
                    "Militar Responsável": "texto",
                    "Andamento": "texto"
                })
                st.success("✅ Alterações salvas com sucesso!")
                st.rerun()


    return valores, False
