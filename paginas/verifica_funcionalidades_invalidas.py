import streamlit as st
import os
import re
from funcoes_compartilhadas import conversa_banco

def app():
    st.title("🔍 Verificação de Caminhos de Funcionalidades")

    st.info("Este verificador analisa os caminhos das funcionalidades cadastradas e alerta sobre erros comuns.")

    funcionalidades = conversa_banco.select("funcionalidades", {
        "ID": "id",
        "Nome": "texto",
        "Caminho": "texto",
    })

    funcionalidades["Caminho"] = funcionalidades["Caminho"].astype(str)
    problemas = []

    for i, row in funcionalidades.iterrows():
        caminho = row["Caminho"]
        id_func = row["ID"]
        nome = row["Nome"]

        # ─── Regras de validação ───────────────────────────────
        if " " in caminho:
            problemas.append((id_func, nome, caminho, "Contém espaço"))
            continue

        if caminho.endswith(".py"):
            problemas.append((id_func, nome, caminho, "Não deve incluir .py"))
            continue

        if not re.match(r'^[a-zA-Z0-9_.]+$', caminho):
            problemas.append((id_func, nome, caminho, "Caracteres inválidos"))
            continue

        # ─── Verifica se o arquivo existe na estrutura ──────────
        caminho_arquivo = f"paginas/{caminho.replace('.', '/')}.py"
        if not os.path.exists(caminho_arquivo):
            problemas.append((id_func, nome, caminho, f"Arquivo não encontrado: {caminho_arquivo}"))

    if problemas:
        st.error("❌ Foram encontradas funcionalidades com problemas:")
        for id_func, nome, caminho, erro in problemas:
            st.markdown(f"""
🔻 **ID:** `{id_func}`  
🏷️ **Nome:** `{nome}`  
📂 **Caminho:** `{caminho}`  
⚠️ **Erro:** {erro}  
---
""")
    else:
        st.success("✅ Todos os caminhos de funcionalidades estão corretos!")
