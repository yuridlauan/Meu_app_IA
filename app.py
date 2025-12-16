import streamlit as st
import importlib
import sys
import streamlit.components.v1 as components

st.write("✅ Importações básicas concluídas.")

from paginas import atualizar_ids
from funcoes_compartilhadas import conversa_banco
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, clear_caches
from funcoes_compartilhadas.controle_acesso import (
    login,
    usuario_logado,
    menus_liberados,
    logoutX,
    require_login, 
)

st.write("✅ Módulos e funções importados com sucesso.")

# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def carregar_menus():
    return conversa_banco.select("menus", {
        "ID": "id",
        "Nome": "texto",
        "Ordem": "numero100",
    })

@st.cache_data
def carregar_funcionalidades():
    return conversa_banco.select("funcionalidades", {
        "ID": "id",
        "ID_Menu": "texto",
        "Nome": "texto",
        "Caminho": "texto",
    })

st.write("✅ Funções de cache definidas.")

# ──────────────────────────────────────────────────────────────────────────────
query_params = st.query_params.to_dict()
if query_params.get("recuperar") == "1":
    st.write("🔁 Modo recuperação de senha ativado")
    mod = reload_module("paginas.redefinir_senha")
    mod.app()
    st.stop()

st.write("✅ Query params verificados.")

st.set_page_config(
    page_title="Meu App com I.A.",
    page_icon="⚡",
    layout="wide"
)

st.write("✅ Configuração da página aplicada.")

aplicar_estilo_padrao()
st.write("✅ Estilo padrão aplicado.")

# HTML ajustes
components.html(
    """<script>
      const root = parent.document.documentElement;
      root.setAttribute('lang', 'pt-BR');
      root.setAttribute('translate', 'no');
      const meta = parent.document.createElement('meta');
      meta.name = 'google';
      meta.content = 'notranslate';
      parent.document.head.appendChild(meta);
    </script>""",
    height=0,
)

st.write("✅ HTML customizado.")

# Título dinâmico da aba
def set_tab_title(title: str, icon_url: str | None = None):
    js = f"""<script>document.title = "{title}";"""
    if icon_url:
        js += f"""
        const link = document.querySelector('link[rel*="icon"]')
            || document.createElement('link');
        link.type = 'image/png';
        link.rel = 'shortcut icon';
        link.href = '{icon_url}';
        document.head.appendChild(link);
        """
    js += "</script>"
    st.markdown(js, unsafe_allow_html=True)

# 🔐 LOGIN
st.write("🔐 Iniciando controle de login...")
require_login()
st.write("✅ Login realizado ou validado.")

# SIDEBAR
st.write("📥 Carregando menus e funcionalidades...")
menus = carregar_menus()
funcionalidades = carregar_funcionalidades()
st.write("✅ Menus e funcionalidades carregados.")

# Continuação do código...
menus = menus.sort_values(by="Ordem")
st.write("✅ Menus ordenados.")

permissoes = menus_liberados()
st.write(f"✅ Permissões carregadas: {permissoes}")

if permissoes is not None:
    funcionalidades = funcionalidades[
        funcionalidades["ID"].astype(str).isin(
            [str(p["ID_Funcionalidade"]) for p in permissoes]
        )
    ]
    st.write("✅ Funcionalidades filtradas por permissões.")

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

st.write(f"✅ Menus disponíveis: {list(menu_disponivel.keys())}")

if not menu_disponivel:
    st.warning("⚠️ Você não tem acesso a nenhum menu.")
    st.stop()

# SIDEBAR – MENU
st.sidebar.image("imagens/logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

area = st.sidebar.selectbox("Área:", list(menu_disponivel.keys()))
st.write(f"✅ Área selecionada: {area}")

funcionalidades_disp = menu_disponivel[area]
rotulo = st.sidebar.radio(
    "Funcionalidade:",
    ["Selecionar..."] + list(funcionalidades_disp.values()),
    index=0
)
st.write(f"✅ Funcionalidade selecionada: {rotulo}")

logoutX()
st.write("✅ Logout exibido no sidebar.")

if rotulo == "Selecionar...":
    st.write("ℹ️ Nenhuma funcionalidade selecionada ainda.")
    st.stop()

# CORPO DO APP
arquivo = next(k for k, v in funcionalidades_disp.items() if v == rotulo)
set_tab_title(f"{rotulo} — Meu App")
st.write(f"✅ Carregando módulo: paginas.{arquivo}")

try:
    mod = __import__(f"paginas.{arquivo}", fromlist=["app"])
    mod.app()
    st.write("✅ Módulo carregado com sucesso.")
except Exception as e:
    st.error(f"❌ Erro ao carregar a página '{arquivo}': {e}")
    st.write("📛 Detalhes do erro:", e)
