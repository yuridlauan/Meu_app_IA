import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credenciais_json = st.secrets["gdrive_credenciais"]

gc = gspread.authorize(Credentials.from_service_account_info(credenciais_json, scopes=scopes))
abas = [ws.title for ws in planilha.worksheets()]
st.write("✅ Conectado com sucesso às abas:", abas)
