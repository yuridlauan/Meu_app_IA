# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from funcoes_compartilhadas import conversa_banco

TABELA = "permissoes"
TIPOS = {
    "ID": "id",
    "ID_Usuario": "texto",
    "ID_Funcionalidade": "texto",
}

def app():
    st.subheader("🔑 Gerenciar Permissões de Usuário")

    # 🔍 Busca usuários cadastrados (exceto admin)
    df_usuarios = conversa_banco.select("usuarios", {
        "ID": "id", "Nome": "texto", "Email": "texto", "Senha": "texto"
    })

    df_usuarios = df_usuarios[df_usuarios["ID"] != "ADMIN"]

    opcoes_usuarios = {
        f'{row["Nome"]} ({row["Email"]})': row["ID"]
        for _, row in df_usuarios.iterrows()
    }

    usuario_selecionado = st.selectbox("👤 Selecione um Usuário", list(opcoes_usuarios.keys()))

    if not usuario_selecionado:
        st.stop()

    usuario_id = opcoes_usuarios[usuario_selecionado]
    st.markdown("---")

    # 🔍 Traz todas funcionalidades agrupadas por menu
    df_funcionalidades = conversa_banco.select("funcionalidades", {
        "ID": "id",
        "ID_Menu": "texto",
        "Nome": "texto",
        "Caminho": "texto",
    })
    df_menus = conversa_banco.select("menus", {
        "ID": "id",
        "Nome": "texto",
        "Ordem": "numero100",
    }).sort_values("Ordem")

    # 🔍 Permissões atuais desse usuário
    df_permissoes = conversa_banco.select(TABELA, TIPOS)
    permissoes_atuais = df_permissoes[df_permissoes["ID_Usuario"] == usuario_id]
    ids_func_atuais = permissoes_atuais["ID_Funcionalidade"].astype(str).tolist()

    st.subheader("🔍 Permissões Atuais")
    if permissoes_atuais.empty:
        st.info("Nenhuma permissão cadastrada para este usuário.")
    else:
        # Mostra o nome da funcionalidade para visualização
        nomes_func = df_funcionalidades.set_index("ID")["Nome"].to_dict()
        permissoes_atuais = permissoes_atuais.copy()
        permissoes_atuais["Funcionalidade"] = permissoes_atuais["ID_Funcionalidade"].map(nomes_func)
        st.dataframe(permissoes_atuais[["ID_Funcionalidade", "Funcionalidade"]], use_container_width=True)

    st.markdown("---")
    st.subheader("✅ Definir Permissões")

    # Checkboxes para cada funcionalidade, agrupadas por menu
    selecao_check = {}
    with st.container(border=True):
        for _, menu in df_menus.iterrows():
            st.markdown(f"**{menu['Nome']}**")
            funcs = df_funcionalidades[df_funcionalidades["ID_Menu"] == menu["ID"]]
            for _, func in funcs.iterrows():
                key = f"check_{func['ID']}"
                marcado = (str(func["ID"]) in ids_func_atuais or st.session_state.get(key, False))
                selecao_check[str(func["ID"])] = st.checkbox(f"{func['Nome']} [{func['Caminho']}]", value=marcado, key=key)

    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Selecionar Tudo"):
            for _, func in df_funcionalidades.iterrows():
                st.session_state[f"check_{func['ID']}"] = True
            st.experimental_rerun()

    if st.button("💾 Salvar Permissões"):
        # Apaga permissões antigas desse usuário
        linhas_apagadas = df_permissoes[df_permissoes["ID_Usuario"] == usuario_id]
        for _, linha in linhas_apagadas.iterrows():
            conversa_banco.delete(
                TABELA,
                where=f"ID,eq,{linha['ID']}",
                tipos_colunas=TIPOS,
            )

        # Insere novas permissões apenas com os IDs corretos
        novos = []
        for id_func, marcado in selecao_check.items():
            if marcado:
                novos.append({
                    "ID_Usuario": usuario_id,
                    "ID_Funcionalidade": id_func,
                })

        if novos:
            conversa_banco.insert(TABELA, pd.DataFrame(novos))

        st.success("✅ Permissões atualizadas com sucesso.")
        st.cache_data.clear()
        st.rerun()
