# -*- coding: utf-8 -*-
# app.py – carrega páginas Streamlit com controle de login e menu por permissões

import streamlit as st
import importlib
import sys
import streamlit.components.v1 as components
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, clear_caches
from funcoes_compartilhadas.controle_acesso import login, usuario_logado, menus_liberados, logoutX
from funcoes_compartilhadas import conversa_banco

# ─── Redireciona para redefinir senha se necessário ───────────────────────────
from urllib.parse import parse_qs
def _query_params_dict() -> dict:
    qp = getattr(st, "query_params", None)
    if qp is not None:
        try:
            return qp.to_dict()
        except Exception:
            try:
                return dict(qp)
            except Exception:
                return {}
    # fallback para versões antigas
    try:
        return st.experimental_get_query_params()
    except Exception:
        return {}


query_params = _query_params_dict()
if query_params.get("recuperar") == "1":


    mod = importlib.reload(importlib.import_module("paginas.redefinir_senha"))
    mod.app()
    st.stop()

# ─── Configuração inicial ─────────────────────────────────────────────────────
st.set_page_config(page_title="Meu App com I.A.", page_icon="⚡", layout="wide")
aplicar_estilo_padrao()

# ─── Estilo do menu lateral ──────────────────────────────────────────────────
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

components.html("""
    <script>
      const root = parent.document.documentElement;
      root.setAttribute('lang', 'pt-BR');
      root.setAttribute('translate', 'no');
      const meta = parent.document.createElement('meta');
      meta.name    = 'google';
      meta.content = 'notranslate';
      parent.document.head.appendChild(meta);
    </script>
""", height=0)

# ─── Utilitários ──────────────────────────────────────────────────────────────
def reload_module(path: str):
    if path in sys.modules:
        return importlib.reload(sys.modules[path])
    return importlib.import_module(path)

def mudar_pagina(alvo: str):
    if st.session_state.get("page") != alvo:
        st.session_state["page"] = alvo
        clear_caches()
        st.rerun()

# ─── Login obrigatório ────────────────────────────────────────────────────────
if not usuario_logado():
    login()
    st.stop()

# ─── MENU LATERAL ─────────────────────────────────────────────────────────────

# 🔍 Busca menus e funcionalidades disponíveis no banco
menus = conversa_banco.select("menus", {"ID": "id", "Nome": "texto", "Ordem": "numero100"})
funcionalidades = conversa_banco.select("funcionalidades", {
    "ID": "id",
    "ID_Menu": "texto",
    "Nome": "texto",
    "Caminho": "texto",
})

menus = menus.sort_values("Ordem")

# 🔐 Filtra funcionalidades com base nas permissões do usuário
permissoes = menus_liberados()
if permissoes is not None:
    funcionalidades = funcionalidades[
        funcionalidades["ID"].astype(str).isin(
            [str(p["ID_Funcionalidade"]) for p in permissoes]
        )
    ]

# 🔗 Agrupa funcionalidades por menu
menu_disponivel = {}
for _, menu in menus.iterrows():
    itens = funcionalidades[funcionalidades["ID_Menu"].astype(str) == str(menu["ID"])]
    if not itens.empty:
        menu_disponivel[menu["Nome"]] = {
            row["Caminho"]: row["Nome"]
            for _, row in itens.iterrows()
        }

if not menu_disponivel:
    st.warning("⚠️ Você não tem acesso a nenhum menu.")
    st.stop()

# ─── Construção visual do menu ────────────────────────────────────────────────
st.sidebar.image("imagens/logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

area = st.sidebar.selectbox("Área:", list(menu_disponivel.keys()))
funcionalidades_disp = menu_disponivel[area]
rotulo = st.sidebar.radio(
    "Funcionalidade:",
    ["Selecionar..."] + list(funcionalidades_disp.values()),
    index=0
)

logoutX()  # 🔒 Botão sair no final do menu lateral

if rotulo == "Selecionar...":
    st.stop()

# 🔄 Carrega e executa a página selecionada
arquivo = next(k for k, v in funcionalidades_disp.items() if v == rotulo)
modulo = reload_module(f"paginas.{arquivo}")
modulo.app()
