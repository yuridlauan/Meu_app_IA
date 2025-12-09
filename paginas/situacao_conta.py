# -*- coding: utf-8 -*-
import streamlit as st
from funcoes_compartilhadas.estilos import set_page_title

def app():
    # ----------------------------------------------------------------
    # Header
    # ----------------------------------------------------------------
    set_page_title("Situação da Conta")

    saldo = st.number_input("Digite o saldo da sua conta (R$):", step=0.01)

    if st.button("Verificar Situação"):
        if saldo > 0:
            st.success(f"Saldo R$ {saldo:.2f} — conta no VERDE")
        
        elif saldo == 0:
            st.info("Saldo zerado.")
        else:
            st.error(f"Saldo R$ {saldo:.2f} — conta no VERMELHO")
