import streamlit as st

def sidebar_menu(options=None, default=None):
    """
    Renderiza o menu lateral principal e retorna a página selecionada.
    options: lista de opções do menu (por padrão inclui Inicio, Tabela de Dados, Configurações)
    """
    st.sidebar.title("Menu")
    if options is None:
        options = ["Inicio", "Tabela de Dados", "Configurações"]
    try:
        index = options.index(default) if default in options else 0
    except ValueError:
        index = 0
    selected = st.sidebar.radio("Escolha a Página", options, index=index)
    return selected

def render_filters(df):
    """
    Renderiza os filtros que dependem do dataframe (ano, empresa).
    Retorna (ano_selecionado, empresa_selecionada).
    """
    st.sidebar.header('Filtros')

    # Ano
    anos_disponiveis = sorted(df['ano'].unique().tolist()) if df is not None and 'ano' in df.columns else []
    anos_disponiveis = [str(a) for a in anos_disponiveis]
    anos_disponiveis.insert(0, 'Todos os Anos')
    ano_selecionado = st.sidebar.selectbox('Selecione o Ano', anos_disponiveis)

    # Empresa (se existir)
    if df is not None and 'cd_multi_empresa' in df.columns:
        empresas_disponiveis = sorted(df['cd_multi_empresa'].unique().tolist())
        empresas_disponiveis = [str(e) for e in empresas_disponiveis]
        empresas_disponiveis.insert(0, 'Todas as Empresas')
        empresa_selecionada = st.sidebar.selectbox('Selecione a Empresa', empresas_disponiveis)
    else:
        empresa_selecionada = 'Todas as Empresas'

    return ano_selecionado, empresa_selecionada