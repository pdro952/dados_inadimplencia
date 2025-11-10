import streamlit as st
import pandas as pd

from sidebar import sidebar_menu
from utils import (
    PASTA_DADOS,
    encontrar_arquivo_csv,
    carregar_dataframe_csv,
    valida_login,
)

# páginas
from pages.inicio import pagina_principal
from pages.dados import pagina_dados_brutos
from pages.config import pagina_configuracoes

# Configurações da página
st.set_page_config(layout="wide", page_title="Hospital MaterDei - Análise Particular")

def main():
    # Validação do usuário
    if not valida_login():
        # valida_login já faz st.stop() se necessário; aqui apenas garantia
        return

    # Carregamento de dados (tenta arquivo 'totais_mensais.csv' ou primeiro CSV encontrado)
    caminho = encontrar_arquivo_csv(PASTA_DADOS, 'totais_mensais.csv')
    if caminho is None:
        # tenta qualquer CSV da pasta
        caminho = encontrar_arquivo_csv(PASTA_DADOS)

    df = None
    if caminho:
        df = carregar_dataframe_csv(caminho)
    else:
        st.warning("Nenhum arquivo CSV encontrado na pasta de dados. Algumas funcionalidades estarão desabilitadas.")

    page = sidebar_menu(options=["Inicio", "Tabela de Dados", "Configurações"], default="Inicio")

    if page == "Inicio":
        pagina_principal(df)
    elif page == "Tabela de Dados":
        pagina_dados_brutos(df)
    elif page == "Configurações":
        pagina_configuracoes()

if __name__ == "__main__":
    main()