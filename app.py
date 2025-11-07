from datetime import datetime, timedelta
from io import BytesIO
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import humanize as hu

# Configuração da página do Streamlit
st.set_page_config(layout="wide")

# Define o caminho para a subpasta onde os CSVs estão localizados
PASTA_DADOS = 'dados_csv'
PASTA_SALVOS = os.path.join(PASTA_DADOS, 'dados_salvos')
ARQUIVO_SALVOS = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_12_meses.csv')
ARQUIVO_SALVOS_MAIS_DE_12_MESES = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_mais_de_12_meses.csv')
ARQUIVO_SALVOS_CA = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_12_meses_ca.csv')
ARQUIVO_SALVOS_MAIS_DE_12_MESES_CA = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_mais_de_12_meses_ca.csv')

def formatar_numero_abreviado(valor):
    """Formata um número em uma string abreviada (ex: 1.5M, 250k)."""
    texto = hu.intword(valor)
    if "million" in texto:
        return texto.replace(" million", "M").replace(".0", "")
    elif "thousand" in texto:
        return texto.replace(" thousand", "k").replace(".0", "")
    return str(valor)

def to_excel(df):
    """
    Converte um DataFrame do pandas para um arquivo Excel na memória.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data

#Validação se usuário está logado na central de aplicações
def valida_login():
    from streamlit_cookies_manager import CookieManager

    cookies = CookieManager()
    if not cookies.ready():
        st.write("Aguardando inicialização dos cookies...")
        st.stop()

    usuario = cookies.get('username')
    token = cookies.get('token')

    url = f"https://central.hmaterdei.com.br:3001/api/menuPapel/usuario/{usuario}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url=url,headers=headers,verify="./.cert/cert.pem")
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            st.markdown(
                """
                <meta http-equiv="refresh" content="0; url=https://central.hmaterdei.com.br/">
                """,
                unsafe_allow_html=True
            )
            st.stop()
    for i in response.json():
        if i.get('CD_PAPEL') == 24 and i.get('CD_SISTEMA') == 10:
            return True
    return False

# --- Leitura dos Arquivos Locais ---
# Cria a pasta 'dados_salvos' se ela não existir
if not os.path.exists(PASTA_SALVOS):
    os.makedirs(PASTA_SALVOS)

# Função para encontrar um arquivo CSV específico na pasta
def encontrar_arquivo_csv(pasta, nome_arquivo=None):
    """
    Procura por um arquivo .csv na pasta especificada.
    Se nome_arquivo for fornecido, busca por esse arquivo específico.
    Caso contrário, retorna o primeiro .csv que encontrar.
    """
    try:
        arquivos = os.listdir(pasta)
        
        if nome_arquivo:
            if nome_arquivo in arquivos:
                return os.path.join(pasta, nome_arquivo)
            else:
                return None
        else:
            # Encontra o primeiro CSV que não seja 'totais_mensais.csv'
            arquivos_csv = [f for f in arquivos if f.endswith('.csv') and f != 'totais_mensais.csv']
            if arquivos_csv:
                return os.path.join(pasta, arquivos_csv[0])
            else:
                return None
    except FileNotFoundError:
        return None

# Funções para salvar os dados editados (Últimos 12 meses)
def salvar_dados_editados(df_editado):
    """Salva o DataFrame editado em um arquivo CSV."""
    try:
        df_editado.to_csv(ARQUIVO_SALVOS, index=False, encoding='latin1')
        st.success("Dados dos últimos 12 meses salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")

def salvar_dados_editados_ca(df_editado): #dados contas abertas
    """Salva o DataFrame editado em um arquivo CSV."""
    try:
        df_editado.to_csv(ARQUIVO_SALVOS_CA, index=False, encoding='latin1')
        st.success("Dados dos últimos 12 meses salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")

def carregar_dados_editados():
    """Carrega o arquivo CSV de dados editados, se existir."""
    if os.path.exists(ARQUIVO_SALVOS):
        try:
            return pd.read_csv(ARQUIVO_SALVOS, encoding='latin1')
        except Exception as e:
            st.warning(f"Erro ao carregar o arquivo de dados salvos (12 meses): {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def carregar_dados_editados_ca():
    """Carrega o arquivo CSV de dados editados, se existir."""
    if os.path.exists(ARQUIVO_SALVOS_CA):
        try:
            return pd.read_csv(ARQUIVO_SALVOS_CA, encoding='latin1')
        except Exception as e:
            st.warning(f"Erro ao carregar o arquivo de dados salvos (12 meses): {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Funções para salvar os dados editados (Mais de 12 meses)
def salvar_dados_mais_de_12_meses(df_editado):
    """Salva o DataFrame editado de inadimplentes com mais de 12 meses."""
    try:
        df_editado.to_csv(ARQUIVO_SALVOS_MAIS_DE_12_MESES, index=False, encoding='latin1')
        st.success("Dados de mais de 12 meses salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados de mais de 12 meses: {e}")

def salvar_dados_mais_de_12_meses_ca(df_editado):
    """Salva o DataFrame editado de inadimplentes com mais de 12 meses."""
    try:
        df_editado.to_csv(ARQUIVO_SALVOS_MAIS_DE_12_MESES_CA, index=False, encoding='latin1')
        st.success("Dados de mais de 12 meses salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados de mais de 12 meses: {e}")

def carregar_dados_mais_de_12_meses():
    """Carrega o arquivo CSV de dados editados com mais de 12 meses, se existir."""
    if os.path.exists(ARQUIVO_SALVOS_MAIS_DE_12_MESES):
        try:
            return pd.read_csv(ARQUIVO_SALVOS_MAIS_DE_12_MESES, encoding='latin1')
        except Exception as e:
            st.warning(f"Erro ao carregar o arquivo de dados salvos (> 12 meses): {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def carregar_dados_mais_de_12_meses_ca():
    """Carrega o arquivo CSV de dados editados com mais de 12 meses, se existir."""
    if os.path.exists(ARQUIVO_SALVOS_MAIS_DE_12_MESES_CA):
        try:
            return pd.read_csv(ARQUIVO_SALVOS_MAIS_DE_12_MESES_CA, encoding='latin1')
        except Exception as e:
            st.warning(f"Erro ao carregar o arquivo de dados salvos (> 12 meses): {e}")
            return pd.DataFrame()
    return pd.DataFrame()

class Principal:
    def pagina_principal(self):
        # Título da aplicação
        st.title('Hospital MaterDei - Análise Particular')

        # --- Processamento do Arquivo de Totais Mensais ---
        caminho_arquivo_totais = encontrar_arquivo_csv(PASTA_DADOS, 'totais_mensais.csv')
        df_totais_mensais = None # Inicializa o dataframe como None

        if caminho_arquivo_totais:
            try:
                df_totais_mensais = pd.read_csv(caminho_arquivo_totais, sep=',', encoding='latin1')
                
                df_totais_mensais['data_mes'] = pd.to_datetime(df_totais_mensais['mes_ano'], errors='coerce', dayfirst=True)
                df_totais_mensais['mes_ano'] = pd.to_datetime(df_totais_mensais['mes_ano'], dayfirst=True).dt.strftime('%Y-%m')
                df_totais_mensais['ano'] = df_totais_mensais['data_mes'].dt.year.astype(str)
                
                if 'vl_total' in df_totais_mensais.columns:
                    df_totais_mensais.rename(columns={'vl_total': 'valor'}, inplace=True)

                if 'cd_multi_empresa' in df_totais_mensais.columns:
                    df_totais_mensais['cd_multi_empresa'] = df_totais_mensais['cd_multi_empresa'].astype(str)

            except Exception as e:
                st.warning(f"Ocorreu um erro ao processar o arquivo 'totais_mensais.csv': {e}")
                st.info("O arquivo será ignorado, mas a análise principal continuará.")
        else:
            st.info("Arquivo 'totais_mensais.csv' não encontrado. Os gráficos mensais não exibirão a linha de percentual.")


        # --- Processamento do Arquivo Principal ---
        caminho_arquivo_principal = encontrar_arquivo_csv(PASTA_DADOS)

        if caminho_arquivo_principal is not None:
            df = pd.read_csv(caminho_arquivo_principal, sep=',', encoding='latin1', low_memory=False)

            # --- Tratamento e Limpeza dos Dados (Arquivo Principal) ---
            df['dt_atendimento'] = pd.to_datetime(df['dt_atendimento'], errors='coerce', dayfirst=True)
            df.dropna(subset=['dt_atendimento'], inplace=True)
            df['ano'] = df['dt_atendimento'].dt.year.astype(str)
            df['mes'] = df['dt_atendimento'].dt.strftime('%Y-%m')
            for col in ['vl_total_conta', 'vl_duplicata', 'vl_soma_recebido', 'vl_em_aberto']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            df.fillna({'vl_em_aberto': 0}, inplace=True)
            if 'cd_multi_empresa' in df.columns:
                df['cd_multi_empresa'] = df['cd_multi_empresa'].astype(str)
            if 'sn_fechada' in df.columns:
                df['sn_fechada'] = df['sn_fechada'].astype(str).str.upper()
            else:
                st.error("A coluna 'sn_fechada' não foi encontrada no arquivo. O quadro resumo não será exibido.")
                st.stop()

            # --- Interface do Usuário na Barra Lateral ---
            st.sidebar.header('Filtros')
            anos_disponiveis = sorted(df['ano'].unique().tolist())
            anos_disponiveis.insert(0, 'Todos os Anos')
            ano_selecionado = st.sidebar.selectbox('Selecione o Ano', anos_disponiveis)
            if 'cd_multi_empresa' in df.columns:
                empresas_disponiveis = sorted(df['cd_multi_empresa'].unique().tolist())
                empresas_disponiveis.insert(0, 'Todas as Empresas')
                empresa_selecionada = st.sidebar.selectbox('Selecione a Empresa', empresas_disponiveis)
            else:
                st.sidebar.warning("A coluna 'cd_multi_empresa' não foi encontrada no arquivo.")
                empresa_selecionada = 'Todas as Empresas'

            # --- Filtra o Dataframe
            df_filtrado = df.copy()
            if ano_selecionado != 'Todos os Anos':
                df_filtrado = df_filtrado[df_filtrado['ano'] == ano_selecionado]
            if empresa_selecionada != 'Todas as Empresas':
                df_filtrado = df_filtrado[df_filtrado['cd_multi_empresa'] == empresa_selecionada]

            # --- Quadro Resumo ---
            if df_filtrado.empty:
                st.warning(f"Não foram encontrados registros para os filtros selecionados.")
            else:
                st.markdown("<h4 style='text-align: center;'>Quadro Resumo de Inadimplência por Ano</h4>", unsafe_allow_html=True)
                df_aberto = df_filtrado[df_filtrado['sn_fechada'] == 'N']
                df_aberto_agg = df_aberto.groupby('ano')['vl_em_aberto'].sum().reset_index()
                df_aberto_agg.rename(columns={'vl_em_aberto': 'Valor Contas em Aberto'}, inplace=True)
                df_inadimplente_agg = df_filtrado[df_filtrado['sn_fechada'] == 'S'].groupby('ano')['vl_em_aberto'].sum().reset_index()
                df_inadimplente_agg.rename(columns={'vl_em_aberto': 'Valor Inadimplente'}, inplace=True)
                quadro_resumo = pd.merge(df_aberto_agg, df_inadimplente_agg, on='ano', how='outer')
                quadro_resumo.fillna(0, inplace=True)
                quadro_resumo['Total'] = quadro_resumo['Valor Contas em Aberto'] + quadro_resumo['Valor Inadimplente']
                if len(quadro_resumo['ano']) > 1:
                    total_row = pd.DataFrame([{'ano': 'Total', 'Valor Contas em Aberto': quadro_resumo['Valor Contas em Aberto'].sum(), 'Valor Inadimplente': quadro_resumo['Valor Inadimplente'].sum(), 'Total': quadro_resumo['Total'].sum()}])
                    quadro_resumo = pd.concat([quadro_resumo, total_row], ignore_index=True)
                cols_formatar = ['Valor Contas em Aberto', 'Valor Inadimplente', 'Total']
                def formatar_moeda(x):
                    try:
                        return f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
                    except (ValueError, TypeError): return x
                for col in cols_formatar:
                        quadro_resumo[col] = quadro_resumo[col].apply(formatar_moeda)
                st.table(quadro_resumo.set_index('ano'))

            #df_inadimplencia = df_filtrado.copy()
            df_ultimos_12_meses = df_filtrado.copy()
            #df_inadimplencia = df_inadimplencia[df_inadimplencia['sn_fechada'] == 'S'] #validar se vai filtrar contas fechadas ou não
            df_ultimos_12_meses['dt_atendimento'] = pd.to_datetime(df_ultimos_12_meses['dt_atendimento'])
            df_ultimos_12_meses.sort_values(by='dt_atendimento', inplace=True)
            data_recente = df_ultimos_12_meses['dt_atendimento'].max()
            data_12_meses_atras = data_recente - pd.DateOffset(months=12)
            df_ultimos_12_meses = df_ultimos_12_meses[df_ultimos_12_meses['dt_atendimento'] >= data_12_meses_atras].copy()

            if not df_ultimos_12_meses.empty:
                st.subheader('Inadimplência - Contas fechadas de pacientes com alta')
                st.markdown("<h4 style='text-align: center;'>Visão Mensal da Inadimplência (Últimos 12 Meses)</h4>", unsafe_allow_html=True)
                df_ultimos_12_meses.loc[:, 'mes'] = df_ultimos_12_meses['dt_atendimento'].dt.strftime('%Y-%m')
                col1, col2 = st.columns(2)

                df_totais_mensal_agg = None
                if df_totais_mensais is not None and not df_totais_mensais.empty:
                    df_totais_filtrado = df_totais_mensais.copy()
                    if ano_selecionado != 'Todos os Anos':
                        df_totais_filtrado = df_totais_filtrado[df_totais_filtrado['ano'] == ano_selecionado]
                    if empresa_selecionada != 'Todas as Empresas':
                        df_totais_filtrado = df_totais_filtrado[df_totais_filtrado['cd_multi_empresa'] == empresa_selecionada]

                    df_totais_filtrado['data_mes'] = pd.to_datetime(df_totais_filtrado['data_mes'])
                    df_totais_filtrado.sort_values(by='data_mes', inplace=True)
                    max_data = df_totais_filtrado['data_mes'].max()
                    data_12_meses = max_data - pd.DateOffset(months=12)

                    df_totais_mensal_agg = df_totais_filtrado[df_totais_filtrado['data_mes'] >= data_12_meses]
                    
                    df_totais_mensal_agg = df_totais_mensal_agg.groupby('mes_ano').agg(
                        total_valor=('valor', 'sum'),
                        total_quantidade=('qtd_contas', 'sum')
                    ).reset_index()
                    df_totais_mensal_agg.rename(columns={'mes_ano': 'mes'}, inplace=True)
                    
                
                with col1: # Gráfico de VALOR
                    st.markdown("**Valores**")
                    inadimplencia_mensal_valor = df_ultimos_12_meses.groupby(['mes', 'tp_atendimento'])['vl_em_aberto'].sum().reset_index()
                    valores_por_tp = df_ultimos_12_meses.groupby(['tp_atendimento'])['vl_em_aberto'].sum().reset_index()

                    total_geral_inadimplencia = valores_por_tp['vl_em_aberto'].sum()

                    total_geral_atendimentos = 0
                    if df_totais_mensal_agg is not None and not df_totais_mensal_agg.empty:
                        total_geral_atendimentos = df_totais_mensal_agg['total_valor'].sum()

                    percentual_inadimplencia = 0
                    if total_geral_atendimentos > 0:
                        percentual_inadimplencia = (total_geral_inadimplencia / total_geral_atendimentos) * 100
                    
                    cols = st.columns(len(valores_por_tp)+2)

                    for i, row in valores_por_tp.iterrows():
                        with cols[i]:
                            st.markdown(f"{row['tp_atendimento']}")
                            st.write(f"**R$ {formatar_numero_abreviado(row['vl_em_aberto'])}**")

                    with cols[len(valores_por_tp)]:
                        st.markdown("Total")
                        st.write(f"**R$ {formatar_numero_abreviado(total_geral_inadimplencia)}**")

                    with cols[len(valores_por_tp) + 1]:
                        st.markdown("% Inadimp.")
                        st.write(f"**{percentual_inadimplencia:.2f}%**")

                    fig_mensal_valor = px.bar(inadimplencia_mensal_valor, 
                                                x='mes', 
                                                y='vl_em_aberto', 
                                                color='tp_atendimento', 
                                                title='Valor em Aberto (R$) vs. % Total', 
                                                labels={'mes': 'Mês', 'vl_em_aberto': 'Valor em Aberto (R$)'}, 
                                                text_auto='.2s')
                    df_totais_barra = inadimplencia_mensal_valor.groupby('mes')['vl_em_aberto'].sum().reset_index()
                    for index, row in df_totais_barra.iterrows():
                        fig_mensal_valor.add_annotation(x=row['mes'], 
                                                        y=row['vl_em_aberto'], 
                                                        text=f"<b>{formatar_numero_abreviado(row['vl_em_aberto'])}</b>", 
                                                        showarrow=False, 
                                                        yshift=25, 
                                                        font=dict(size=12, color="black"))
                    
                    if df_totais_mensal_agg is not None:
                        df_comparativo_valor = pd.merge(df_totais_barra, df_totais_mensal_agg, on='mes', how='left')
                        df_comparativo_valor['percentual'] = (df_comparativo_valor['vl_em_aberto'] / df_comparativo_valor['total_valor']).fillna(0) * 100
                        
                        # CÁLCULO PARA POSICIONAR A LINHA ACIMA DAS BARRAS
                        max_bar_value = df_totais_barra['vl_em_aberto'].max()
                        # Mapeia o percentual para uma faixa de valores no topo do gráfico
                        df_comparativo_valor['y_posicao_linha'] = max_bar_value * 1 + (df_comparativo_valor['percentual'] / 100) * (max_bar_value * 1.5)
                        
                        text_labels = df_comparativo_valor['percentual'].apply(lambda x: f'{x:.1f}%')

                        fig_mensal_valor.add_trace(go.Scatter(
                            x=df_comparativo_valor['mes'],
                            y=df_comparativo_valor['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',  
                            text=text_labels,          
                            textposition='top center', 
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))
                    
                    fig_mensal_valor.update_layout(
                        yaxis_range=[0, df_totais_barra['vl_em_aberto'].max() * 1.5], 
                        legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_mensal_valor)
                
                with col2: # Gráfico de QUANTIDADE
                    st.markdown("**Quantidades**")
                    inadimplencia_mensal_qtd = df_ultimos_12_meses.groupby(['mes','tp_atendimento']).size().reset_index(name='quantidade')
                    quantidade_por_tp = df_ultimos_12_meses.groupby(['tp_atendimento']).size().reset_index(name='quantidade')

                    quantidade_total_inadimplencia = quantidade_por_tp['quantidade'].sum()

                    quantidade_total_geral = 0
                    if df_totais_mensal_agg is not None and not df_totais_mensal_agg.empty:
                        quantidade_total_geral = df_totais_mensal_agg['total_quantidade'].sum()

                    percentual_quantidade = 0
                    if quantidade_total_geral > 0:
                        percentual_quantidade = (quantidade_total_inadimplencia / quantidade_total_geral) * 100

                    cols = st.columns(len(quantidade_por_tp)+2)

                    for i, row in quantidade_por_tp.iterrows():
                        with cols[i]:
                            st.markdown(f"{row['tp_atendimento']}")
                            st.write(f"**{row['quantidade']}**")
                    
                    with cols[len(quantidade_por_tp)]:
                        st.markdown("Qtde. Total")
                        st.write(f"**{quantidade_total_inadimplencia}**")

                    with cols[len(quantidade_por_tp)+1]:
                        st.markdown("% Inadimp.")
                        st.write(f"**{percentual_quantidade:.2f}%**")

                    fig_mensal_qtd = px.bar(inadimplencia_mensal_qtd, 
                                            x='mes', 
                                            y='quantidade', 
                                            color='tp_atendimento', 
                                            title='Qtd. Contas Inadimplentes vs. % Total', 
                                            labels={'mes': 'Mês', 'quantidade': 'Quantidade de Contas'}, 
                                            text_auto=True)
                    
                    if df_totais_mensal_agg is not None:
                        df_totais_barra_qtd = inadimplencia_mensal_qtd.groupby('mes')['quantidade'].sum().reset_index()
                        df_comparativo_qtd = pd.merge(df_totais_barra_qtd, df_totais_mensal_agg, on='mes', how='left')
                        df_comparativo_qtd['percentual'] = (df_comparativo_qtd['quantidade'] / df_comparativo_qtd['total_quantidade']).fillna(0) * 100

                        valor_maximo_barra = df_totais_barra_qtd['quantidade'].max()
                        df_comparativo_qtd['y_posicao_linha'] = valor_maximo_barra * 1 + (df_comparativo_qtd['percentual'] / 100) * (valor_maximo_barra * 1.1)
                        
                        text_labels_qtd = df_comparativo_qtd['percentual'].apply(lambda x: f'{x:.1f}%')

                        fig_mensal_qtd.add_trace(go.Scatter(
                            x=df_comparativo_qtd['mes'],
                            y=df_comparativo_qtd['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',
                            text=text_labels_qtd,      
                            textposition='top center', 
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))

                        annotations = []
                        for _, row in df_totais_barra_qtd.iterrows():
                            annotations.append(
                                dict(
                                    x=row['mes'],
                                    y=row['quantidade'],
                                    xref="x",
                                    yref="y",
                                    text=f"<b>{row['quantidade']}</b>",
                                    showarrow=False,
                                    yshift=25,
                                    font=dict(size=12, color='black')
                                )
                            )

                    fig_mensal_qtd.update_layout(yaxis_range=[0, df_totais_barra_qtd['quantidade'].max() * 1.5],
                                                    legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5),annotations=annotations)
                    st.plotly_chart(fig_mensal_qtd)
                
                # --- Top 15 Inadimplentes (Últimos 12 meses)---
                st.markdown("<h4 style='text-align: center;'>Top Ofensores - Últimos 12 meses</h4>", unsafe_allow_html=True)

                idx_ultima_data = df_ultimos_12_meses.loc[df_ultimos_12_meses.groupby('cd_paciente')['dt_atendimento'].idxmax()]

                df_agrupado_soma = df_ultimos_12_meses.groupby('cd_paciente')['vl_em_aberto'].sum().reset_index()
                colunas_para_manter = [col for col in df_ultimos_12_meses.columns if col not in ['vl_em_aberto']]
                df_ultima_data_campos = idx_ultima_data[colunas_para_manter]

                df_final = pd.merge(
                    df_agrupado_soma,
                    df_ultima_data_campos,
                    on='cd_paciente',
                    how='left'
                )
                #df_final = df_final.rename(columns={'vl_em_aberto': 'vl_em_aberto_total'})
                
                #top_15_inadimplentes = df_ultimos_12_meses.groupby(['cd_paciente', 'tp_atendimento', 'dt_atendimento','tipo'])['vl_em_aberto'].sum().reset_index()
                top_15_inadimplentes = df_final.nlargest(15, 'vl_em_aberto')

                colunas_finais = ['cd_paciente', 'tp_atendimento', 'dt_atendimento', 'tipo', 'vl_em_aberto']
                top_15_inadimplentes = top_15_inadimplentes[colunas_finais]
                
                df_dados_salvos = carregar_dados_editados()
                if not df_dados_salvos.empty:
                    top_15_inadimplentes = pd.merge(
                        top_15_inadimplentes,
                        df_dados_salvos[['cd_paciente', 'causa', 'status_atual']], 
                        on='cd_paciente', 
                        how='left'
                    )
                else:
                    top_15_inadimplentes = top_15_inadimplentes.assign(
                        causa = '',
                        status_atual = ''
                    )
                top_15_inadimplentes.fillna('', inplace=True)
                top_15_inadimplentes['dt_atendimento'] = pd.to_datetime(top_15_inadimplentes['dt_atendimento']).dt.strftime('%m/%Y')
                
                edited_df = st.data_editor(
                    top_15_inadimplentes,
                    column_order=[
                        "cd_paciente", "vl_em_aberto", "tp_atendimento",
                        "dt_atendimento", "tipo", "causa", "status_atual"
                    ],
                    column_config={
                        "cd_paciente": "Código Paciente",
                        "vl_em_aberto": st.column_config.NumberColumn("Valor em Aberto", format="R$ %.2f"),
                        "tp_atendimento": "Tipo de Atendimento",
                        "dt_atendimento": "Data Atendimento",
                        "tipo": "Tipo",
                        "causa": st.column_config.TextColumn("Causa", help="Descreva a causa da inadimplência", width="large"),
                        "status_atual": st.column_config.TextColumn("Status Atual", help="Status atual da negociação", width="medium")
                    },
                    disabled=["cd_paciente", "vl_em_aberto", "tp_atendimento", "dt_atendimento", "tipo"],
                    hide_index=True,
                    use_container_width=True,
                    key="tabela_editavel_12_meses"
                )

                if st.button("Salvar Edições",key="Salvar_ate_12_meses"):
                    salvar_dados_editados(edited_df)

            else:
                st.warning("Não há dados de inadimplência nos últimos 12 meses.")
                    
            # --- Gráficos Anuais ---
            st.markdown("<h4 style='text-align: center;'>Visão Anual da Inadimplência</h4>",unsafe_allow_html=True)

            # Garantindo que o filtro de ano não afete a análise anual
            df_anual = df.copy()
            #df_anual = df_anual[df_anual['sn_fechada']=='S'] #ANALISANDO SOMENTE CONTAS FECHADAS

            # Aplica o filtro de empresa se ele existir
            if 'cd_multi_empresa' in df_anual.columns and empresa_selecionada != 'Todas as Empresas':
                df_anual = df_anual[df_anual['cd_multi_empresa'] == empresa_selecionada]

            # Agrupa os dados anuais de inadimplência
            inadimplencia_anual_valor = df_anual[df_anual['vl_em_aberto'] > 0].groupby(['ano', 'tp_atendimento'])['vl_em_aberto'].sum().reset_index()
            inadimplencia_anual_qtd = df_anual[df_anual['vl_em_aberto'] > 0].groupby(['ano', 'tp_atendimento']).size().reset_index(name='quantidade')

            # Valores de contas extras
            df_conta_extra_anual = df_anual[df_anual['tipo'] == 'CONTA EXTRA']
            conta_extra_anual_valor = df_conta_extra_anual[df_conta_extra_anual['vl_em_aberto'] > 0].groupby(['ano'])['vl_em_aberto'].sum().reset_index()
            conta_extra_anual_valor = conta_extra_anual_valor.rename(columns={'vl_em_aberto': 'total_extra'})
            conta_extra_anual_qtd = df_conta_extra_anual[df_conta_extra_anual['vl_em_aberto'] > 0].groupby(['ano']).size().reset_index(name='quantidade_extra')
            

            # Processa os dados totais anuais, ignorando o filtro de ano
            df_totais_anual = None
            if df_totais_mensais is not None and not df_totais_mensais.empty:
                df_totais_filtrado_anual = df_totais_mensais.copy()
                if 'cd_multi_empresa' in df_totais_filtrado_anual.columns and empresa_selecionada != 'Todas as Empresas':
                    df_totais_filtrado_anual = df_totais_filtrado_anual[df_totais_filtrado_anual['cd_multi_empresa'] == empresa_selecionada]
                
                df_totais_anual = df_totais_filtrado_anual.copy()
                df_totais_anual['ano'] = df_totais_anual['mes_ano'].str[:4]
                df_totais_anual = df_totais_anual.groupby('ano').agg(
                    total_valor=('valor', 'sum'),
                    total_quantidade=('qtd_contas', 'sum')
                ).reset_index()

            if not inadimplencia_anual_valor.empty:
                col1, col2 = st.columns(2)
                
                with col1: # Gráfico de VALOR
                    fig_anual_valor = px.bar(inadimplencia_anual_valor, 
                                            x='ano', 
                                            y='vl_em_aberto', 
                                            color='tp_atendimento', 
                                            title='Valor em Aberto por Ano e Tipo de Atendimento', 
                                            labels={'ano': 'Ano', 'vl_em_aberto': 'Valor em Aberto (R$)'}, 
                                            text_auto='.2s')
                    
                    # Adiciona o total acima de cada barra
                    df_totais_inadimplencia_ano = inadimplencia_anual_valor.groupby('ano')['vl_em_aberto'].sum().reset_index()
                    #percentual contas extras
                    conta_extra_anual_valor = pd.merge(conta_extra_anual_valor, df_totais_inadimplencia_ano, on='ano', how='left')
                    conta_extra_anual_valor['percentual'] = (conta_extra_anual_valor['total_extra'] / conta_extra_anual_valor['vl_em_aberto']).fillna(0) * 100
                    for index, row in df_totais_inadimplencia_ano.iterrows():
                        fig_anual_valor.add_annotation(x=row['ano'], 
                                                    y=row['vl_em_aberto'], 
                                                    text=f"<b>R$ {formatar_numero_abreviado(row['vl_em_aberto'])}</b>", 
                                                    showarrow=False, 
                                                    yshift=25, 
                                                    font=dict(size=12, color="black"))
                    
                    for index, row in conta_extra_anual_valor.iterrows():
                        fig_anual_valor.add_annotation(x=row['ano'],
                                                        y= 0,
                                                        text=f"<b>Conta Extra: {formatar_numero_abreviado(row['total_extra'])}</b><br><b>({row['percentual']:.1f}%)</b>",
                                                        showarrow=False,
                                                        yshift=-35,
                                                        font=dict(size=10, color="black"))
                    
                    # Adiciona a linha de percentual de inadimplência
                    if df_totais_anual is not None and not df_totais_anual.empty:
                        df_comparativo_anual_valor = pd.merge(df_totais_inadimplencia_ano, df_totais_anual, on='ano', how='left')
                        df_comparativo_anual_valor['percentual'] = (df_comparativo_anual_valor['vl_em_aberto'] / df_comparativo_anual_valor['total_valor']).fillna(0) * 100
                        
                        max_bar_value = df_totais_inadimplencia_ano['vl_em_aberto'].max()
                        df_comparativo_anual_valor['y_posicao_linha'] = max_bar_value * 1 + (df_comparativo_anual_valor['percentual'] / 100) * (max_bar_value * 1.5)
                        
                        text_labels = df_comparativo_anual_valor['percentual'].apply(lambda x: f'{x:.1f}%')

                        fig_anual_valor.add_trace(go.Scatter(
                            x=df_comparativo_anual_valor['ano'],
                            y=df_comparativo_anual_valor['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',
                            text=text_labels,
                            textposition='top center',
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))
                        
                        fig_anual_valor.update_layout(
                            yaxis_range=[0, df_totais_inadimplencia_ano['vl_em_aberto'].max() * 1.5]
                        )
                        
                    fig_anual_valor.update_layout(
                        legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_anual_valor)
                
                with col2: # Gráfico de QUANTIDADE
                    fig_anual_qtd = px.bar(inadimplencia_anual_qtd, 
                                        x='ano', 
                                        y='quantidade', 
                                        color='tp_atendimento', 
                                        title='Quantidade de Contas Inadimplentes por Ano e Tipo de Atendimento', 
                                        labels={'ano': 'Ano', 'quantidade': 'Quantidade de Contas'}, 
                                        text_auto=True)
                    
                    # Adiciona o total acima de cada barra
                    df_totais_inadimplencia_qtd = inadimplencia_anual_qtd.groupby('ano')['quantidade'].sum().reset_index()
                    conta_extra_anual_qtd = pd.merge(conta_extra_anual_qtd, df_totais_inadimplencia_qtd, on='ano', how='left')
                    conta_extra_anual_qtd['percentual'] = (conta_extra_anual_qtd['quantidade_extra'] / conta_extra_anual_qtd['quantidade']).fillna(0) * 100
                    for index, row in df_totais_inadimplencia_qtd.iterrows():
                        fig_anual_qtd.add_annotation(x=row['ano'], 
                                                    y=row['quantidade'], 
                                                    text=f"<b>{row['quantidade']}</b>", 
                                                    showarrow=False, 
                                                    yshift=30, 
                                                    font=dict(size=12, color="black"))
                    
                    for index, row in conta_extra_anual_qtd.iterrows():
                        fig_anual_qtd.add_annotation(x=row['ano'],
                                                        y=0,
                                                        text=f"<b>Conta Extra: {row['quantidade_extra']}</b><br><b>({row['percentual']:.1f}%)</b>",
                                                        showarrow=False,
                                                        yshift=-35,
                                                        font=dict(size=10, color="black"))
                    
                    # Adiciona a linha de percentual de inadimplência
                    if df_totais_anual is not None and not df_totais_anual.empty:
                        df_comparativo_anual_qtd = pd.merge(df_totais_inadimplencia_qtd, df_totais_anual, on='ano', how='left')
                        df_comparativo_anual_qtd['percentual'] = (df_comparativo_anual_qtd['quantidade'] / df_comparativo_anual_qtd['total_quantidade']).fillna(0) * 100
                        
                        valor_maximo_barra = df_totais_inadimplencia_qtd['quantidade'].max()
                        df_comparativo_anual_qtd['y_posicao_linha'] = valor_maximo_barra * 1.15 + (df_comparativo_anual_qtd['percentual'] / 100) * (valor_maximo_barra * 1.5)
                        
                        text_labels_qtd = df_comparativo_anual_qtd['percentual'].apply(lambda x: f'{x:.1f}%')
                        
                        fig_anual_qtd.add_trace(go.Scatter(
                            x=df_comparativo_anual_qtd['ano'],
                            y=df_comparativo_anual_qtd['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',
                            text=text_labels_qtd,
                            textposition='top center',
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))
                        
                        fig_anual_qtd.update_layout(
                            yaxis_range=[0, df_totais_inadimplencia_qtd['quantidade'].max() * 1.5]
                        )
                        
                    fig_anual_qtd.update_layout(
                        legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_anual_qtd)
            else:
                st.info("Sem dados Anuais")

            # --- Top 15 Inadimplentes (Mais de 12 meses) ---
            st.markdown("<h4 style='text-align: center;'>Top Ofensores - Mais de 12 meses</h4>", unsafe_allow_html=True)

            data_mais_de_12_meses = data_recente - pd.DateOffset(days=365)
                # Garantindo que o filtro de ano não afete a análise anual
            df_mais_de_12_meses = df.copy()
            #df_mais_de_12_meses = df_mais_de_12_meses[df_mais_de_12_meses['sn_fechada']=='S'] #ANALISANDO SOMENTE CONTAS FECHADAS
            df_mais_de_12_meses = df_mais_de_12_meses[df_mais_de_12_meses['dt_atendimento'] < data_mais_de_12_meses].copy()

            # Aplica o filtro de empresa se ele existir
            if 'cd_multi_empresa' in df_mais_de_12_meses.columns and empresa_selecionada != 'Todas as Empresas':
                df_mais_de_12_meses = df_mais_de_12_meses[df_mais_de_12_meses['cd_multi_empresa'] == empresa_selecionada]

            if not df_mais_de_12_meses.empty:
                idx_ultima_data = df_mais_de_12_meses.loc[df_mais_de_12_meses.groupby('cd_paciente')['dt_atendimento'].idxmax()]

                df_agrupado_soma = df_mais_de_12_meses.groupby('cd_paciente')['vl_em_aberto'].sum().reset_index()
                colunas_para_manter = [col for col in df_mais_de_12_meses.columns if col not in ['vl_em_aberto']]
                df_ultima_data_campos = idx_ultima_data[colunas_para_manter]

                df_final = pd.merge(
                    df_agrupado_soma,
                    df_ultima_data_campos,
                    on='cd_paciente',
                    how='left'
                )
                #top_15_mais_de_12_meses = df_mais_de_12_meses.groupby(['cd_paciente', 'tp_atendimento', 'dt_atendimento','tipo'])['vl_em_aberto'].sum().reset_index()
                top_15_mais_de_12_meses = df_final.nlargest(15, 'vl_em_aberto')

                df_dados_salvos_antigos = carregar_dados_mais_de_12_meses()
                if not df_dados_salvos_antigos.empty:
                    top_15_mais_de_12_meses = pd.merge(
                        top_15_mais_de_12_meses,
                        df_dados_salvos_antigos[['cd_paciente', 'causa', 'status_atual']],
                        on='cd_paciente',
                        how='left'
                    )
                else:
                    top_15_mais_de_12_meses = top_15_mais_de_12_meses.assign(
                        causa='',
                        status_atual=''
                    )

                for col in ['causa', 'status_atual']:
                    top_15_mais_de_12_meses[col] = top_15_mais_de_12_meses[col].fillna('').astype(str)

                top_15_mais_de_12_meses['dt_atendimento'] = pd.to_datetime(top_15_mais_de_12_meses['dt_atendimento']).dt.strftime('%m/%Y')

                edited_df_antigos = st.data_editor(
                    top_15_mais_de_12_meses,
                    column_order=[
                        "cd_paciente", "vl_em_aberto", "tp_atendimento",
                        "dt_atendimento", "tipo", "causa", "status_atual"
                    ],
                    column_config={
                        "cd_paciente": "Código Paciente",
                        "vl_em_aberto": st.column_config.NumberColumn("Valor em Aberto", format="R$ %.2f"),
                        "tp_atendimento": "Tipo de Atendimento",
                        "dt_atendimento": "Data Atendimento",
                        "tipo": "Tipo",
                        "causa": st.column_config.TextColumn("Causa", help="Descreva a causa da inadimplência", width="large"),
                        "status_atual": st.column_config.TextColumn("Status Atual", help="Status atual da negociação", width="medium")
                    },
                    disabled=["cd_paciente", "vl_em_aberto", "tp_atendimento", "dt_atendimento", "tipo"],
                    hide_index=True,
                    use_container_width=True,
                    key="tabela_editavel_mais_de_12_meses"
                )

                if st.button("Salvar Edições",key="Salvar_maior_12_meses"):
                    salvar_dados_mais_de_12_meses(edited_df_antigos)
            else:
                st.warning("Não há dados de inadimplência com mais de 12 meses.")  

            # A partir daqui serão dados de contas abertas e pacientes com alta
            st.subheader('Inadimplência - Contas Abertas de pacientes com alta')
                
            df_contas_abertas_12_meses = df_filtrado.copy()
            df_contas_abertas_12_meses = df_contas_abertas_12_meses[df_contas_abertas_12_meses['sn_fechada'] == 'N'] #retira contas fechadas
            #df_contas_abertas.dropna(subset=['dt_alta'], inplace=True) #retira contas sem data de alta

            df_contas_abertas_12_meses['dt_atendimento'] = pd.to_datetime(df_contas_abertas_12_meses['dt_atendimento'])
            df_contas_abertas_12_meses.sort_values(by='dt_atendimento', inplace=True)
            
            #separa um dataframe com os ultimos 12 meses (já filtrado)
            data_recente_contas_abertas = df_contas_abertas_12_meses['dt_atendimento'].max()
            data_12_meses_atras_abertas = data_recente_contas_abertas - pd.DateOffset(months=12)
            df_contas_abertas_12_meses = df_contas_abertas_12_meses[df_contas_abertas_12_meses['dt_atendimento'] >= data_12_meses_atras_abertas].copy()

            if not df_contas_abertas_12_meses.empty:
                st.markdown("<h4 style='text-align: center;'>Visão Mensal Contas Abertas</h4>", unsafe_allow_html=True)

                df_contas_abertas_12_meses.loc[:, 'mes'] = df_contas_abertas_12_meses['dt_atendimento'].dt.strftime('%Y-%m')
                col1, col2 = st.columns(2)

                df_totais_mensal_agg = None
                if df_totais_mensais is not None and not df_totais_mensais.empty:
                    df_totais_filtrado = df_totais_mensais.copy()
                    if ano_selecionado != 'Todos os Anos':
                        df_totais_filtrado = df_totais_filtrado[df_totais_filtrado['ano'] == ano_selecionado]
                    if empresa_selecionada != 'Todas as Empresas':
                        df_totais_filtrado = df_totais_filtrado[df_totais_filtrado['cd_multi_empresa'] == empresa_selecionada]

                    df_totais_filtrado['data_mes'] = pd.to_datetime(df_totais_filtrado['data_mes'])
                    df_totais_filtrado.sort_values(by='data_mes', inplace=True)
                    max_data = df_totais_filtrado['data_mes'].max()
                    data_12_meses = max_data - pd.DateOffset(months=12)

                    df_totais_mensal_agg = df_totais_filtrado[df_totais_filtrado['data_mes'] >= data_12_meses]
                    
                    df_totais_mensal_agg = df_totais_mensal_agg.groupby('mes_ano').agg(
                        total_valor=('valor', 'sum'),
                        total_quantidade=('qtd_contas', 'sum')
                    ).reset_index()
                    df_totais_mensal_agg.rename(columns={'mes_ano': 'mes'}, inplace=True)
                
                with col1: # Gráfico de VALOR
                    st.markdown("**Valores**")
                    inadimplencia_mensal_valor = df_contas_abertas_12_meses.groupby(['mes', 'tp_atendimento'])['vl_em_aberto'].sum().reset_index()
                    valores_por_tp = df_contas_abertas_12_meses.groupby(['tp_atendimento'])['vl_em_aberto'].sum().reset_index()

                    total_geral_inadimplencia = valores_por_tp['vl_em_aberto'].sum()

                    total_geral_atendimentos = 0
                    if df_totais_mensal_agg is not None and not df_totais_mensal_agg.empty:
                        total_geral_atendimentos = df_totais_mensal_agg['total_valor'].sum()

                    percentual_inadimplencia = 0
                    if total_geral_atendimentos > 0:
                        percentual_inadimplencia = (total_geral_inadimplencia / total_geral_atendimentos) * 100
                    
                    cols = st.columns(len(valores_por_tp)+2)

                    for i, row in valores_por_tp.iterrows():
                        with cols[i]:
                            st.markdown(f"{row['tp_atendimento']}")
                            st.write(f"**R$ {formatar_numero_abreviado(row['vl_em_aberto'])}**")

                    with cols[len(valores_por_tp)]:
                        st.markdown("Total")
                        st.write(f"**R$ {formatar_numero_abreviado(total_geral_inadimplencia)}**")

                    with cols[len(valores_por_tp) + 1]:
                        st.markdown("% Inadimp.")
                        st.write(f"**{percentual_inadimplencia:.2f}%**")

                    fig_mensal_valor = px.bar(inadimplencia_mensal_valor, 
                                                x='mes', 
                                                y='vl_em_aberto', 
                                                color='tp_atendimento', 
                                                title='Valor em Aberto (R$) vs. % Total', 
                                                labels={'mes': 'Mês', 'vl_em_aberto': 'Valor em Aberto (R$)'}, 
                                                text_auto='.2s')
                    df_totais_barra = inadimplencia_mensal_valor.groupby('mes')['vl_em_aberto'].sum().reset_index()
                    for index, row in df_totais_barra.iterrows():
                        fig_mensal_valor.add_annotation(x=row['mes'], 
                                                        y=row['vl_em_aberto'], 
                                                        text=f"<b>{formatar_numero_abreviado(row['vl_em_aberto'])}</b>", 
                                                        showarrow=False, 
                                                        yshift=25, 
                                                        font=dict(size=12, color="black"))
                    
                    if df_totais_mensal_agg is not None:
                        df_comparativo_valor = pd.merge(df_totais_barra, df_totais_mensal_agg, on='mes', how='left')
                        df_comparativo_valor['percentual'] = (df_comparativo_valor['vl_em_aberto'] / df_comparativo_valor['total_valor']).fillna(0) * 100
                        
                        # CÁLCULO PARA POSICIONAR A LINHA ACIMA DAS BARRAS
                        max_bar_value = df_totais_barra['vl_em_aberto'].max()
                        # Mapeia o percentual para uma faixa de valores no topo do gráfico
                        df_comparativo_valor['y_posicao_linha'] = max_bar_value * 1.2 + (df_comparativo_valor['percentual'] / 100) * (max_bar_value * 1.5)
                        
                        text_labels = df_comparativo_valor['percentual'].apply(lambda x: f'{x:.1f}%')

                        fig_mensal_valor.add_trace(go.Scatter(
                            x=df_comparativo_valor['mes'],
                            y=df_comparativo_valor['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',  
                            text=text_labels,          
                            textposition='top center', 
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))
                    
                    fig_mensal_valor.update_layout(
                        yaxis_range=[0, df_totais_barra['vl_em_aberto'].max() * 1.5], 
                        legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5))
                    st.plotly_chart(fig_mensal_valor)
                
                with col2: # Gráfico de QUANTIDADE
                    st.markdown("**Quantidades**")
                    inadimplencia_mensal_qtd = df_contas_abertas_12_meses.groupby(['mes','tp_atendimento']).size().reset_index(name='quantidade')
                    quantidade_por_tp = df_contas_abertas_12_meses.groupby(['tp_atendimento']).size().reset_index(name='quantidade')

                    quantidade_total_inadimplencia = quantidade_por_tp['quantidade'].sum()

                    quantidade_total_geral = 0
                    if df_totais_mensal_agg is not None and not df_totais_mensal_agg.empty:
                        quantidade_total_geral = df_totais_mensal_agg['total_quantidade'].sum()

                    percentual_quantidade = 0
                    if quantidade_total_geral > 0:
                        percentual_quantidade = (quantidade_total_inadimplencia / quantidade_total_geral) * 100

                    cols = st.columns(len(quantidade_por_tp)+2)

                    for i, row in quantidade_por_tp.iterrows():
                        with cols[i]:
                            st.markdown(f"{row['tp_atendimento']}")
                            st.write(f"**{row['quantidade']}**")
                    
                    with cols[len(quantidade_por_tp)]:
                        st.markdown("Qtde. Total")
                        st.write(f"**{quantidade_total_inadimplencia}**")

                    with cols[len(quantidade_por_tp)+1]:
                        st.markdown("% Inadimp.")
                        st.write(f"**{percentual_quantidade:.2f}%**")

                    fig_mensal_qtd = px.bar(inadimplencia_mensal_qtd, 
                                            x='mes', 
                                            y='quantidade', 
                                            color='tp_atendimento', 
                                            title='Qtd. Contas Inadimplentes vs. % Total', 
                                            labels={'mes': 'Mês', 'quantidade': 'Quantidade de Contas'}, 
                                            text_auto=True)
                    
                    if df_totais_mensal_agg is not None:
                        df_totais_barra_qtd = inadimplencia_mensal_qtd.groupby('mes')['quantidade'].sum().reset_index()
                        df_comparativo_qtd = pd.merge(df_totais_barra_qtd, df_totais_mensal_agg, on='mes', how='left')
                        df_comparativo_qtd['percentual'] = (df_comparativo_qtd['quantidade'] / df_comparativo_qtd['total_quantidade']).fillna(0) * 100

                        valor_maximo_barra = df_totais_barra_qtd['quantidade'].max()
                        df_comparativo_qtd['y_posicao_linha'] = valor_maximo_barra * 1 + (df_comparativo_qtd['percentual'] / 100) * (valor_maximo_barra * 1.1)
                        
                        text_labels_qtd = df_comparativo_qtd['percentual'].apply(lambda x: f'{x:.1f}%')

                        fig_mensal_qtd.add_trace(go.Scatter(
                            x=df_comparativo_qtd['mes'],
                            y=df_comparativo_qtd['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',
                            text=text_labels_qtd,      
                            textposition='top center', 
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))

                        annotations = []
                        for _, row in df_totais_barra_qtd.iterrows():
                            annotations.append(
                                dict(
                                    x=row['mes'],
                                    y=row['quantidade'],
                                    xref="x",
                                    yref="y",
                                    text=f"<b>{row['quantidade']}</b>",
                                    showarrow=False,
                                    yshift=25,
                                    font=dict(size=12, color='black')
                                )
                            )

                    fig_mensal_qtd.update_layout(yaxis_range=[0, df_totais_barra_qtd['quantidade'].max() * 1.5],
                                                    legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5),annotations=annotations)
                    st.plotly_chart(fig_mensal_qtd)

                ## TOP 15 CONTAS ABERTAS ultimos 12 meses
                st.markdown("<h4 style='text-align: center;'>Top Ofensores - Últimos 12 meses</h4>", unsafe_allow_html=True)

                df_aux = df_contas_abertas_12_meses.copy()
                df_aux['dt_atendimento'] = pd.to_datetime(df_aux['dt_atendimento']).dt.strftime('%m/%Y')

                idx_ultima_data = df_aux.loc[df_aux.groupby('cd_paciente')['dt_atendimento'].idxmax()]

                df_agrupado_soma = df_aux.groupby('cd_paciente')['vl_em_aberto'].sum().reset_index()
                colunas_para_manter = [col for col in df_aux.columns if col not in ['vl_em_aberto']]
                df_ultima_data_campos = idx_ultima_data[colunas_para_manter]

                df_final = pd.merge(
                    df_agrupado_soma,
                    df_ultima_data_campos,
                    on='cd_paciente',
                    how='left'
                )

                top_15_inadimplentes_ca = df_final.nlargest(15, 'vl_em_aberto')
                
                df_dados_salvos_ca = carregar_dados_editados_ca()
                if not df_dados_salvos_ca.empty:
                    df_dados_salvos_ca.dropna(subset=['causa', 'status_atual'], how='all', inplace=True)
                    top_15_inadimplentes_ca = pd.merge(
                        top_15_inadimplentes_ca[['cd_paciente', 'tp_atendimento', 'dt_atendimento','tipo','vl_em_aberto']],
                        df_dados_salvos_ca[['cd_paciente', 'dt_atendimento', 'causa', 'status_atual']], 
                        on=['cd_paciente','dt_atendimento'], 
                        how='left'
                    )
                else:
                    top_15_inadimplentes_ca['causa'] = ''
                    top_15_inadimplentes_ca['status_atual'] = ''
                    
                top_15_inadimplentes_ca.fillna({'causa': ''},inplace=True)
                top_15_inadimplentes_ca.fillna({'status_atual': ''},inplace=True)
                
                edited_df_ca = st.data_editor(
                    top_15_inadimplentes_ca,
                    column_order=[
                        "cd_paciente", "vl_em_aberto", "tp_atendimento",
                        "dt_atendimento", "tipo", "causa", "status_atual"
                    ],
                    column_config={
                        "cd_paciente": "Código Paciente",
                        "vl_em_aberto": st.column_config.NumberColumn("Valor em Aberto", format="R$ %.2f"),
                        "tp_atendimento": "Tipo de Atendimento",
                        "dt_atendimento": "Data Atendimento",
                        "tipo": "Tipo",
                        "causa": st.column_config.TextColumn("Causa", help="Descreva a causa da inadimplência", width="large"),
                        "status_atual": st.column_config.TextColumn("Status Atual", help="Status atual da negociação", width="medium")
                    },
                    disabled=["cd_paciente", "vl_em_aberto", "tp_atendimento", "dt_atendimento", "tipo"],
                    hide_index=True,
                    use_container_width=True,
                    key="tabela_editavel_12_meses_ca"
                )

                if st.button("Salvar Edições",key="Salvar_ate_12_meses_ca"):
                    salvar_dados_editados_ca(edited_df_ca)

            # --- Gráficos Anuais de CONTAS ABERTAS---
            st.markdown("<h4 style='text-align: center;'>Visão Anual Contas Abertas</h4>",unsafe_allow_html=True)

            # Garantindo que o filtro de ano não afete a análise anual
            df_anual_ca = df.copy()
            df_anual_ca = df_anual_ca[df_anual_ca['sn_fechada']=='N'] #ANALISANDO SOMENTE CONTAS ABERTAS

            # Aplica o filtro de empresa se ele existir
            if 'cd_multi_empresa' in df_anual_ca.columns and empresa_selecionada != 'Todas as Empresas':
                df_anual_ca = df_anual_ca[df_anual_ca['cd_multi_empresa'] == empresa_selecionada]

            # Agrupa os dados anuais de inadimplência
            inadimplencia_anual_valor_ca = df_anual_ca[df_anual_ca['vl_em_aberto'] > 0].groupby(['ano', 'tp_atendimento'])['vl_em_aberto'].sum().reset_index()
            inadimplencia_anual_qtd = df_anual_ca[df_anual_ca['vl_em_aberto'] > 0].groupby(['ano', 'tp_atendimento']).size().reset_index(name='quantidade')

            # Valores de contas extras
            df_conta_extra_anual = df_anual_ca[df_anual_ca['tipo'] == 'CONTA EXTRA']
            conta_extra_anual_valor = df_conta_extra_anual[df_conta_extra_anual['vl_em_aberto'] > 0].groupby(['ano'])['vl_em_aberto'].sum().reset_index()
            conta_extra_anual_valor = conta_extra_anual_valor.rename(columns={'vl_em_aberto': 'total_extra'})
            conta_extra_anual_qtd = df_conta_extra_anual[df_conta_extra_anual['vl_em_aberto'] > 0].groupby(['ano']).size().reset_index(name='quantidade_extra')
            

            # Processa os dados totais anuais, ignorando o filtro de ano
            df_totais_anual = None
            if df_totais_mensais is not None and not df_totais_mensais.empty:
                df_totais_filtrado_anual = df_totais_mensais.copy()
                if 'cd_multi_empresa' in df_totais_filtrado_anual.columns and empresa_selecionada != 'Todas as Empresas':
                    df_totais_filtrado_anual = df_totais_filtrado_anual[df_totais_filtrado_anual['cd_multi_empresa'] == empresa_selecionada]
                
                df_totais_anual = df_totais_filtrado_anual.copy()
                df_totais_anual['ano'] = df_totais_anual['mes_ano'].str[:4]
                df_totais_anual = df_totais_anual.groupby('ano').agg(
                    total_valor=('valor', 'sum'),
                    total_quantidade=('qtd_contas', 'sum')
                ).reset_index()

            if not inadimplencia_anual_valor_ca.empty:
                col1, col2 = st.columns(2)
                
                with col1: # Gráfico de VALOR
                    fig_anual_valor = px.bar(inadimplencia_anual_valor_ca, 
                                            x='ano', 
                                            y='vl_em_aberto', 
                                            color='tp_atendimento', 
                                            title='Valor em Aberto por Ano e Tipo de Atendimento', 
                                            labels={'ano': 'Ano', 'vl_em_aberto': 'Valor em Aberto (R$)'}, 
                                            text_auto='.2s')
                    
                    # Adiciona o total acima de cada barra
                    df_totais_inadimplencia_ano = inadimplencia_anual_valor_ca.groupby('ano')['vl_em_aberto'].sum().reset_index()
                    #percentual contas extras
                    conta_extra_anual_valor = pd.merge(conta_extra_anual_valor, df_totais_inadimplencia_ano, on='ano', how='left')
                    conta_extra_anual_valor['percentual'] = (conta_extra_anual_valor['total_extra'] / conta_extra_anual_valor['vl_em_aberto']).fillna(0) * 100
                    for index, row in df_totais_inadimplencia_ano.iterrows():
                        fig_anual_valor.add_annotation(x=row['ano'], 
                                                    y=row['vl_em_aberto'], 
                                                    text=f"<b>R$ {formatar_numero_abreviado(row['vl_em_aberto'])}</b>", 
                                                    showarrow=False, 
                                                    yshift=25, 
                                                    font=dict(size=12, color="black"))
                    
                    for index, row in conta_extra_anual_valor.iterrows():
                        fig_anual_valor.add_annotation(x=row['ano'],
                                                        y= 0,
                                                        text=f"<b>Conta Extra: {formatar_numero_abreviado(row['total_extra'])}</b><br><b>({row['percentual']:.1f}%)</b>",
                                                        showarrow=False,
                                                        yshift=-35,
                                                        font=dict(size=10, color="black"))
                    
                    # Adiciona a linha de percentual de inadimplência
                    if df_totais_anual is not None and not df_totais_anual.empty:
                        df_comparativo_anual_valor = pd.merge(df_totais_inadimplencia_ano, df_totais_anual, on='ano', how='left')
                        df_comparativo_anual_valor['percentual'] = (df_comparativo_anual_valor['vl_em_aberto'] / df_comparativo_anual_valor['total_valor']).fillna(0) * 100
                        
                        max_bar_value = df_totais_inadimplencia_ano['vl_em_aberto'].max()
                        df_comparativo_anual_valor['y_posicao_linha'] = max_bar_value * 1 + (df_comparativo_anual_valor['percentual'] / 100) * (max_bar_value * 1.5)
                        
                        text_labels = df_comparativo_anual_valor['percentual'].apply(lambda x: f'{x:.1f}%')

                        fig_anual_valor.add_trace(go.Scatter(
                            x=df_comparativo_anual_valor['ano'],
                            y=df_comparativo_anual_valor['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',
                            text=text_labels,
                            textposition='top center',
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))
                        
                        fig_anual_valor.update_layout(
                            yaxis_range=[0, df_totais_inadimplencia_ano['vl_em_aberto'].max() * 1.5]
                        )
                        
                    fig_anual_valor.update_layout(
                        legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_anual_valor)
                
                with col2: # Gráfico de QUANTIDADE
                    fig_anual_qtd = px.bar(inadimplencia_anual_qtd, 
                                        x='ano', 
                                        y='quantidade', 
                                        color='tp_atendimento', 
                                        title='Quantidade de Contas Inadimplentes por Ano e Tipo de Atendimento', 
                                        labels={'ano': 'Ano', 'quantidade': 'Quantidade de Contas'}, 
                                        text_auto=True)
                    
                    # Adiciona o total acima de cada barra
                    df_totais_inadimplencia_qtd = inadimplencia_anual_qtd.groupby('ano')['quantidade'].sum().reset_index()
                    conta_extra_anual_qtd = pd.merge(conta_extra_anual_qtd, df_totais_inadimplencia_qtd, on='ano', how='left')
                    conta_extra_anual_qtd['percentual'] = (conta_extra_anual_qtd['quantidade_extra'] / conta_extra_anual_qtd['quantidade']).fillna(0) * 100
                    for index, row in df_totais_inadimplencia_qtd.iterrows():
                        fig_anual_qtd.add_annotation(x=row['ano'], 
                                                    y=row['quantidade'], 
                                                    text=f"<b>{row['quantidade']}</b>", 
                                                    showarrow=False, 
                                                    yshift=30, 
                                                    font=dict(size=12, color="black"))
                    
                    for index, row in conta_extra_anual_qtd.iterrows():
                        fig_anual_qtd.add_annotation(x=row['ano'],
                                                        y=0,
                                                        text=f"<b>Conta Extra: {row['quantidade_extra']}</b><br><b>({row['percentual']:.1f}%)</b>",
                                                        showarrow=False,
                                                        yshift=-35,
                                                        font=dict(size=10, color="black"))
                    
                    # Adiciona a linha de percentual de inadimplência
                    if df_totais_anual is not None and not df_totais_anual.empty:
                        df_comparativo_anual_qtd = pd.merge(df_totais_inadimplencia_qtd, df_totais_anual, on='ano', how='left')
                        df_comparativo_anual_qtd['percentual'] = (df_comparativo_anual_qtd['quantidade'] / df_comparativo_anual_qtd['total_quantidade']).fillna(0) * 100
                        
                        valor_maximo_barra = df_totais_inadimplencia_qtd['quantidade'].max()
                        df_comparativo_anual_qtd['y_posicao_linha'] = valor_maximo_barra * 1.15 + (df_comparativo_anual_qtd['percentual'] / 100) * (valor_maximo_barra * 1.5)
                        
                        text_labels_qtd = df_comparativo_anual_qtd['percentual'].apply(lambda x: f'{x:.1f}%')
                        
                        fig_anual_qtd.add_trace(go.Scatter(
                            x=df_comparativo_anual_qtd['ano'],
                            y=df_comparativo_anual_qtd['y_posicao_linha'],
                            name='% Inadimplência',
                            mode='lines+markers+text',
                            text=text_labels_qtd,
                            textposition='top center',
                            textfont=dict(size=10, color="black"),
                            line=dict(color='red')
                        ))
                        
                        fig_anual_qtd.update_layout(
                            yaxis_range=[0, df_totais_inadimplencia_qtd['quantidade'].max() * 1.5]
                        )
                        
                    fig_anual_qtd.update_layout(
                        legend=dict(title='', orientation="h", yanchor="bottom", y= -0.3, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_anual_qtd)
            else:
                st.info("Sem dados Anuais")
            
            # --- Top 15 Inadimplentes (Mais de 12 meses) ---
            st.markdown("<h4 style='text-align: center;'>Top Ofensores - Contas abertas Mais de 12 meses</h4>", unsafe_allow_html=True)

            data_mais_de_12_meses = data_recente - pd.DateOffset(days=365)
                # Garantindo que o filtro de ano não afete a análise anual
            df_ca_mais_de_12_meses = df.copy()
            df_ca_mais_de_12_meses = df_ca_mais_de_12_meses[df_ca_mais_de_12_meses['sn_fechada']=='N'] #ANALISANDO SOMENTE CONTAS ABERTAS
            df_ca_mais_de_12_meses = df_ca_mais_de_12_meses[df_ca_mais_de_12_meses['dt_atendimento'] < data_mais_de_12_meses].copy()

            # Aplica o filtro de empresa se ele existir
            if 'cd_multi_empresa' in df_ca_mais_de_12_meses.columns and empresa_selecionada != 'Todas as Empresas':
                df_ca_mais_de_12_meses = df_ca_mais_de_12_meses[df_ca_mais_de_12_meses['cd_multi_empresa'] == empresa_selecionada]

            if not df_ca_mais_de_12_meses.empty:
                idx_ultima_data = df_ca_mais_de_12_meses.loc[df_ca_mais_de_12_meses.groupby('cd_paciente')['dt_atendimento'].idxmax()]

                df_agrupado_soma = df_ca_mais_de_12_meses.groupby('cd_paciente')['vl_em_aberto'].sum().reset_index()
                colunas_para_manter = [col for col in df_ca_mais_de_12_meses.columns if col not in ['vl_em_aberto']]
                df_ultima_data_campos = idx_ultima_data[colunas_para_manter]

                df_final = pd.merge(
                    df_agrupado_soma,
                    df_ultima_data_campos,
                    on='cd_paciente',
                    how='left'
                )

                #top_15_mais_de_12_meses = df_ca_mais_de_12_meses.groupby(['cd_paciente', 'tp_atendimento', 'dt_atendimento','tipo'])['vl_em_aberto'].sum().reset_index()
                top_15_mais_de_12_meses = df_final.nlargest(15, 'vl_em_aberto')

                df_dados_salvos_antigos = carregar_dados_mais_de_12_meses_ca()
                if not df_dados_salvos_antigos.empty:
                    top_15_mais_de_12_meses = pd.merge(
                        top_15_mais_de_12_meses,
                        df_dados_salvos_antigos[['cd_paciente', 'causa', 'status_atual']],
                        on=['cd_paciente','dt_atendimento'],
                        how='left'
                    )
                else:
                    top_15_mais_de_12_meses = top_15_mais_de_12_meses.assign(
                        causa='',
                        status_atual=''
                    )

                for col in ['causa', 'status_atual']:
                    top_15_mais_de_12_meses[col] = top_15_mais_de_12_meses[col].fillna('').astype(str)

                top_15_mais_de_12_meses['dt_atendimento'] = pd.to_datetime(top_15_mais_de_12_meses['dt_atendimento']).dt.strftime('%m/%Y')

                edited_df_antigos = st.data_editor(
                    top_15_mais_de_12_meses,
                    column_order=[
                        "cd_paciente", "vl_em_aberto", "tp_atendimento",
                        "dt_atendimento", "tipo", "causa", "status_atual"
                    ],
                    column_config={
                        "cd_paciente": "Código Paciente",
                        "vl_em_aberto": st.column_config.NumberColumn("Valor em Aberto", format="R$ %.2f"),
                        "tp_atendimento": "Tipo de Atendimento",
                        "dt_atendimento": "Data Atendimento",
                        "tipo": "Tipo",
                        "causa": st.column_config.TextColumn("Causa", help="Descreva a causa da inadimplência", width="large"),
                        "status_atual": st.column_config.TextColumn("Status Atual", help="Status atual da negociação", width="medium")
                    },
                    disabled=["cd_paciente", "vl_em_aberto", "tp_atendimento", "dt_atendimento", "tipo"],
                    hide_index=True,
                    use_container_width=True,
                    key="tabela_editavel_mais_de_12_meses_ca"
                )

                if st.button("Salvar Edições",key="Salvar_maior_12_meses_ca"):
                    salvar_dados_mais_de_12_meses_ca(edited_df_antigos)
            else:
                st.warning("Não há dados de inadimplência com mais de 12 meses.")  
    
    def dados_brutos(self):
        caminho_arquivo_principal = encontrar_arquivo_csv(PASTA_DADOS)
        df = pd.read_csv(caminho_arquivo_principal, sep=',', encoding='latin1', low_memory=False)

        # --- Tratamento e Limpeza dos Dados (Arquivo Principal) ---
        df['dt_atendimento'] = pd.to_datetime(df['dt_atendimento'], errors='coerce', dayfirst=True)
        df.dropna(subset=['dt_atendimento'], inplace=True)
        df['ano'] = df['dt_atendimento'].dt.year.astype(str)
        df['mes'] = df['dt_atendimento'].dt.strftime('%Y-%m')
        for col in ['vl_total_conta', 'vl_duplicata', 'vl_soma_recebido', 'vl_em_aberto']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        df.fillna({'vl_em_aberto': 0}, inplace=True)
        df['cd_multi_empresa'] = df['cd_multi_empresa'].astype(str)
        df['sn_fechada'] = df['sn_fechada'].astype(str).str.upper()

        st.dataframe(df, use_container_width=True, hide_index=True)

        excel_data = to_excel(df)
        st.download_button(
            label="Baixar dados em formato Excel",
            data=excel_data,
            file_name='inadimplencia_particular.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def run(self):
        valida = valida_login()
        if valida == True:
            page = st.sidebar.radio(
                "Escolha a Página", 
                ["Inicio", "Tabela de Dados"])
            if page == "Inicio":
                self.pagina_principal()
            elif page == "Tabela de Dados":
                self.dados_brutos()

# Executar o dashboard
if __name__ == "__main__":
    dashboard = Principal()
    dashboard.run()