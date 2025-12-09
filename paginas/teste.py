# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np

# ---------------------- Configuração da Página ----------------------
st.set_page_config(page_title="Teste", layout="wide")

# ---------------------- Título da Página ----------------------
st.title("Teste")

# ---------------------- Criação do DataFrame ----------------------
# Gerando dados aleatórios com números float
df = pd.DataFrame({
    "Produto": ["A", "B", "C", "D", "E"],
    "Preço": np.random.uniform(10, 100, 5).round(2),
    "Imposto (%)": np.random.uniform(5, 20, 5).round(2),
    "Custo Final": np.random.uniform(50, 200, 5).round(2)
})

# ---------------------- Exibir Tabela ----------------------
st.subheader("Tabela de Dados (Números Quebrados)")
st.dataframe(df)
