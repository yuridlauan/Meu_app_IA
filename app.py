# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import sys
import streamlit.components.v1 as components
from paginas import atualizar_ids
from funcoes_compartilhadas.estilos import (
    aplicar_estilo_padrao,
    clear_caches,
)

# ─── 1. Configuração inicial ──────────────────────────────────────
st.set_page_config(page_title="Meu App com I.A.", page_icon="⚡", layout="wide")
aplicar_estilo_padrao()

# Estilo visual para o menu lateral
st.markdown("""
    <style>
    [data-testid="stSidebar"] .stRadio > div {
        flex-direction: column;
        gap: 0.3rem;
    }
    [data-testid="stSidebar"] label {
        align-items: center;
        display: flex;
        gap: 0.5rem;
        word-break: break-word;
    }
    </style>
""", unsafe_allow_html=True)

# Força idioma da página
components.html("""
<script>
  const root = parent.document.documentElement;
  root.setAttribute('lang', 'pt-BR');
  root.setAttribute('translate', 'no');
  const meta = parent.document.createElement('meta');
  meta.name = 'google';
  meta.content = 'notranslate';
  parent.document.head.appendChild(meta);
</script>
""", height=0)

# ─── 2. Funções utilitárias ──────────────────────────────────────
def set_tab_title(title: str, icon_url: str | None = None) -> None:
    js = f"""<script>document.title = "{title}";"""
    if icon_url:
        js += f"""
        const link = document.querySelector('link[rel*="icon"]') || document.createElement('link');
        link.type = 'image/png';
        link.rel  = 'shortcut icon';
        link.href = '{icon_url}';
        document.head.appendChild(link);"""
    js += "</script>"
    st.markdown(js, unsafe_allow_html=True)

def reload_module(path: str):
    if path in sys.modules:
        return importlib.reload(sys.modules[path])
    return importlib.import_module(path)

def mudar_pagina(alvo: str) -> None:
    if st.session_state.get("page") != alvo:
        st.session_state["page"] = alvo
        clear_caches()
        st.rerun()

# ─── 3. Definição manual das páginas ──────────────────────────────
PAGINAS = {
    "Serviço": {
        "porangatu": "Porangatu",
        "santa_tereza": "Santa Tereza",
        "estrela_do_norte": "Estrela do Norte",
        "formoso": "Formoso",
        "trombas": "Trombas",
        "novo_planalto": "Novo Planalto",
        "montividiu": "Montividiu",
        "mutunopolis": "Mutunópolis",
    },
    "Militares": {
        "militares.dlauan": "Asp Of D'Lauan (Admin)",
        "militares.tamilla": "2° Sgt Tamilla",
        "militares.ribeiro": "2° Sgt Ribeiro",
        "militares.ederson": "2° Sgt Éderson"
    },
    "Administrador": {
        "cadastro_usuarios": "Cadastro de Usuários",
        "cadastro_menus": "Cadastro de Menus",
        "cadastro_funcionalidades": "Cadastro de Funcionalidades",
        "cadastro_permissoes": "Cadastro de Permissões",
        "painel_financeiro": "Painel Financeiro",
        "Atualizar IDs": atualizar_ids.app  # executa direto
    }
}

# ─── 4. Menu lateral ───────────────────────────────────────────────
st.sidebar.image("imagens/logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

area = st.sidebar.selectbox("Área:", list(PAGINAS.keys()))
funcionalidades = PAGINAS[area]

rotulo = st.sidebar.radio(
    "Funcionalidade:",
    ["Selecionar..."] + list(funcionalidades.values()),
    index=0
)

if rotulo == "Selecionar...":
    st.stop()

arquivo = next(k for k, v in funcionalidades.items() if v == rotulo)

# ─── 5. Título da aba ──────────────────────────────────────────────
set_tab_title(f"{rotulo} — Meu App")

# ─── 6. Execução da página ─────────────────────────────────────────
if callable(arquivo):
    arquivo()
else:
    mod = reload_module(f"paginas.{arquivo}")
    mod.app()
