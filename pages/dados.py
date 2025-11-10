import streamlit as st
import pandas as pd
from sidebar import render_filters
from utils import salvar_dados_editados, carregar_dados_salvos

def pagina_dados_brutos(df):
    """
    Página 'Tabela de Dados' — tabela editável e opções de salvar.
    Mantive comportamento de edição e salvamento similar ao app original.
    """
    st.title("Tabela de Dados (Bruta)")

    if df is None:
        st.info("Nenhum dado para exibir.")
        return

    ano_selecionado, empresa_selecionada = render_filters(df)

    # Aplica filtros básicos (mesma lógica do inicio)
    df_filtrado = df.copy()
    if ano_selecionado and ano_selecionado != 'Todos os Anos' and 'ano' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['ano'] == str(ano_selecionado)]
    if empresa_selecionada and empresa_selecionada != 'Todas as Empresas' and 'cd_multi_empresa' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['cd_multi_empresa'] == str(empresa_selecionada)]

    st.markdown("### Visualizar e Editar")
    # Exibição simples (substitua por st.data_editor com col configs se preferir)
    st.dataframe(df_filtrado)

    # Se quiser edição inline (como no app original), use st.data_editor (Streamlit versão >=1.20)
    try:
        edited = st.data_editor(df_filtrado, num_rows="dynamic", use_container_width=True, key="editor1")
        if st.button("Salvar Edições"):
            salvar_dados_editados(edited)
    except Exception:
        # fallback: não exibe editor se versão do streamlit não suportar
        st.info("Editor interativo não disponível. Atualize o Streamlit para usar edições inline.")
