# -*- coding: utf-8 -*-
"""
Controle de Acesso Genérico (Streamlit Cloud Friendly)
- Login
- Logout
- Cadastro de Usuário
- Cadastro de Permissões
- Verificação de Acesso

❌ Sem cookies
✅ Apenas session_state
"""

import streamlit as st
import pandas as pd
import hashlib
from funcoes_compartilhadas import conversa_banco
from PIL import Image
import base64
from io import BytesIO

# ──────────────────────────────────────────────────────────────────────────────
# 🖼️ Imagem em base64
def image_base64(path):
    img = Image.open(path)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


# ──────────────────────────────────────────────────────────────────────────────
# 🔐 Tabelas usadas no Google Sheets
TABELA_USUARIOS = "usuarios"
TABELA_PERMISSOES = "permissoes"

TIPOS_USUARIOS = {
    "ID": "id",
    "Nome": "texto",
    "Email": "texto",
    "Senha": "texto",
}

TIPOS_PERMISSOES = {
    "ID": "id",
    "ID_Usuario": "texto",
    "ID_Funcionalidade": "texto",
}


# ──────────────────────────────────────────────────────────────────────────────
# 🔑 Função para criptografar senha
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# 🚪 LOGIN
def login():
    from funcoes_compartilhadas import conversa_banco

    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])

    with col2:
        # Logo
        logo_data = image_base64("imagens/logo.png")
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="{logo_data}" style="width:70%; max-width:240px; margin-bottom:40px" />
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "<h3 style='text-align:center; color:#444;'>Entre no Sistema</h3>",
            unsafe_allow_html=True
        )

        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        # CSS botão
        st.markdown("""
            <style>
            div[data-testid="stButton"] > button {
                display: block;
                margin: 0 auto;
                background-color:#4CAF50;
                color:#ffffff;
                font-size:14px;
                padding:6px 20px;
                border:none;
                border-radius:5px;
            }
            div[data-testid="stButton"] > button:hover {
                background-color:#388E3C;
            }
            </style>
        """, unsafe_allow_html=True)

        
        if st.button("Entrar", key="login_botao"):
            try:
                df = conversa_banco.select(TABELA_USUARIOS, TIPOS_USUARIOS)
            except Exception as e:
                st.error(f"❌ Erro ao acessar banco: {e}")
                return

            df = conversa_banco.select(TABELA_USUARIOS, TIPOS_USUARIOS)
            df = df[df["Email"].str.lower() == email.lower()]

            if df.empty:
                st.error("❌ Usuário não encontrado.")
                return

            senha_hash = hash_senha(senha)
            if df.iloc[0]["Senha"] != senha_hash:
                st.error("❌ Senha incorreta.")
                return

            # ✅ Login OK
            st.session_state["usuario_logado"] = {
                "ID": str(df.iloc[0]["ID"]),
                "Nome": df.iloc[0]["Nome"],
                "Email": df.iloc[0]["Email"],
            }

            st.success(f"✅ Bem-vindo, {df.iloc[0]['Nome']}!")
            st.rerun()

        # Link recuperar senha
        st.markdown("""
            <div style="text-align:center; margin-top:10px">
                <a href="?recuperar=1" style="font-size:12px; color:#777;">
                    Esqueci minha senha
                </a>
            </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 🔓 LOGOUT
def logoutX():
    st.sidebar.markdown("---")

    usuario = st.session_state.get("usuario_logado")
    if isinstance(usuario, dict):
        st.sidebar.markdown(
            f"<div style='text-align:center'><em>Usuário: {usuario.get('Nome','')}</em></div>",
            unsafe_allow_html=True
        )

    if st.sidebar.button("Sair", key="btn_logout_global"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]

        try:
            qp = getattr(st, "query_params", None)
            if qp is not None and hasattr(qp, "clear"):
                qp.clear()
            else:
                # Compatibilidade com versões antigas do Streamlit
                st.experimental_set_query_params()
        except Exception:
            pass

        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# 🛑 Verificar se usuário está logado
def usuario_logado():
    return st.session_state.get("usuario_logado") is not None


# ──────────────────────────────────────────────────────────────────────────────
# ✅ Verificar permissões
def menus_liberados():
    if not usuario_logado():
        return []

    usuario_id = str(st.session_state["usuario_logado"]["ID"])

    # 🔥 Admin vê tudo
    if usuario_id in ["1", "ADMIN", "20251220_152855_192168116_1"]:
        return None

    df = conversa_banco.select(TABELA_PERMISSOES, {
        "ID": "id",
        "ID_Usuario": "texto",
        "ID_Funcionalidade": "texto",
    })

    if df.empty:
        return []

    df = df[df["ID_Usuario"] == usuario_id]
    return df.to_dict(orient="records")
# ──────────────────────────────────────────────────────────────────────────────
# 🔐 Garantir que o usuário esteja logado
def require_login(mensagem: str = "🔒 Sua sessão expirou. Faça login novamente."):
    if not usuario_logado():
        st.warning(mensagem)
        login()
        st.stop()
