# -*- coding: utf-8 -*-
import streamlit as st
import random, string
from funcoes_compartilhadas import conversa_banco
from funcoes_compartilhadas.controle_acesso import hash_senha, image_base64
from funcoes_compartilhadas.envia_email import enviar_email
from funcoes_compartilhadas.estilos import set_page_title



from funcoes_compartilhadas.estilos import (
    aplicar_estilo_padrao,
    clear_caches,
)
aplicar_estilo_padrao()



TABELA_USUARIOS = "usuarios"
TIPOS_USUARIOS = {
    "ID": "id",
    "Nome": "texto",
    "Email": "texto",
    "Senha": "texto",
}

def app():

    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:

        # ─── CSS do botão Enviar ─────────────────────────────────────────
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
                transition: background-color 0.2s ease;
            }
            div[data-testid="stButton"] > button:hover {
                background-color: #388E3C;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)


        # Aplica largura máxima para a área de conteúdo central
        st.markdown("""
            <style>
            .block-container {
                max-width: 100% !important;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)

        # ─── Logo ────────────────────────────────────────────────
        logo_data = image_base64("imagens/logo.png")
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{logo_data}" style="width:70%; max-width:240px; margin-bottom:40px" />
            </div>
            """,
            unsafe_allow_html=True
        )

        # ─── Título ───────────────────────────────────────────────
        st.markdown("<h3 style='text-align:center; color:#444;'>Redefina sua senha</h3>", unsafe_allow_html=True)

        # ─── Campo de email ───────────────────────────────────────
        email = st.text_input("Digite seu e-mail", key="rec_email")

        # ─── Botão enviar ─────────────────────────────────────────
        if st.button("Enviar", key="rec_senha_botao"):
            aviso = st.info("📨 Enviando nova senha... aguarde...")            
            df = conversa_banco.select(TABELA_USUARIOS, TIPOS_USUARIOS)
            df = df[df["Email"].str.lower() == email.lower()]

            if not df.empty:
                nova = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                hash_nova = hash_senha(nova)
                conversa_banco.update(
                    TABELA_USUARIOS, ["Senha"], [hash_nova],
                    where=f"Email,eq,{email}", tipos_colunas=TIPOS_USUARIOS
                )

                # você pode usar o https://tunepit.net/tool/pt/text-to-html
                mensagem = f"""
<p>E ai fera?&nbsp;<br>
<br>Vimos que você pediu para resetar a sua senha.<br>Aqui está: <b>{nova}</b><br>
<br>Use com segurança!<br>
<br>At.te.<br>Equipe Data⚡EVO<br>&nbsp;</p>
                """


                enviar_email(email, "Meu App com I.A. 👉 sua nova senha chegou", mensagem, html=True)
            aviso.empty()
            st.success(f"OK! se o email **{email}** estiver em nossa base, mandaremos uma senha nova para ele.")
