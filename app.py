# -*- coding: utf-8 -*-
import streamlit as st
import importlib
import sys
import streamlit.components.v1 as components


from funcoes_compartilhadas import conversa_banco
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao
from funcoes_compartilhadas.controle_acesso import (
    login,
    usuario_logado,
    menus_liberados,
    logoutX,
)

# ──────────────────────────────────────────────────────────────────────────────
# Configuração inicial (NÃO acessa secrets)
st.set_page_config(
    page_title="Meu App com I.A.",
    page_icon="⚡",
    layout="wide"
)

aplicar_estilo_padrao()

# ──────────────────────────────────────────────────────────────────────────────
# Ajustes visuais do menu
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

# ──────────────────────────────────────────────────────────────────────────────
# Ajustes HTML (idioma)
components.html(
    """
    <script>
      const root = parent.document.documentElement;
      root.setAttribute('lang', 'pt-BR');
      root.setAttribute('translate', 'no');
      const meta = parent.document.createElement('meta');
      meta.name = 'google';
      meta.content = 'notranslate';
      parent.document.head.appendChild(meta);
    </script>
    """,
    height=0,
)

# ──────────────────────────────────────────────────────────────────────────────
# Função para recarregar páginas dinamicamente
def reload_module(path: str):
    if path in sys.modules:
        return importlib.reload(sys.modules[path])
    return importlib.import_module(path)

# ──────────────────────────────────────────────────────────────────────────────
# Recuperação de senha (query param)
query_params = st.query_params.to_dict()
if query_params.get("recuperar") == "1":
    mod = reload_module("paginas.redefinir_senha")
    mod.app()
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 🔐 LOGIN (ANTES DE QUALQUER CONEXÃO COM BANCO)
# 🔐 [LOGIN DESATIVADO TEMPORARIAMENTE]
st.warning("⚠️ LOGIN DESATIVADO TEMPORARIAMENTE PARA DEPURAÇÃO")

# Simula um login manual para continuar o fluxo
st.session_state["usuario_logado"] = {
    "ID": "admin",  # Pode colocar qualquer valor existente na aba usuarios
    "Nome": "Admin",
    "Email": "admin@email.com",
    "Tipo": "admin"
}


# ──────────────────────────────────────────────────────────────────────────────
# 🔗 A PARTIR DAQUI, PODE ACESSAR O BANCO COM SEGURANÇA

def carregar_menus():
    return conversa_banco.select("menus", {
        "ID": "id",
        "Nome": "texto",
        "Ordem": "numero100",
    })

def carregar_funcionalidades():
    return conversa_banco.select("funcionalidades", {
        "ID": "id",
        "ID_Menu": "texto",
        "Nome": "texto",
        "Caminho": "texto",
    })

# ──────────────────────────────────────────────────────────────────────────────
# Carrega menus e permissões
menus = carregar_menus()
funcionalidades = carregar_funcionalidades()

menus = menus.sort_values(by="Ordem")

permissoes = menus_liberados()  # None = admin total

if permissoes is not None:
    funcionalidades = funcionalidades[
        funcionalidades["ID"].astype(str).isin(
            [str(p["ID_Funcionalidade"]) for p in permissoes]
        )
    ]

# ──────────────────────────────────────────────────────────────────────────────
# Monta menu disponível
menu_disponivel = {}

for _, menu in menus.iterrows():
    itens = funcionalidades[
        funcionalidades["ID_Menu"].astype(str) == str(menu["ID"])
    ]

    if not itens.empty:
        menu_disponivel[menu["Nome"]] = {
            row["Caminho"]: row["Nome"]
            for _, row in itens.iterrows()
        }

if not menu_disponivel:
    st.warning("⚠️ Você não tem acesso a nenhum menu.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
st.sidebar.image("imagens/logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

area = st.sidebar.selectbox("Área:", list(menu_disponivel.keys()))

funcionalidades_disp = menu_disponivel[area]

rotulo = st.sidebar.radio(
    "Funcionalidade:",
    ["Selecionar..."] + list(funcionalidades_disp.values()),
    index=0
)

# Logout sempre visível
logoutX()

if rotulo == "Selecionar...":
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# CORPO DO APP
arquivo = next(k for k, v in funcionalidades_disp.items() if v == rotulo)

try:
    mod = reload_module(f"paginas.{arquivo}")
    mod.app()
except Exception as e:
    st.error(f"Erro ao carregar a página '{arquivo}':")
    st.exception(e)
