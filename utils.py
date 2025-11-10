import os
from io import BytesIO
import requests
import pandas as pd
import streamlit as st
import humanize as hu

# Constantes de caminho
PASTA_DADOS = 'dados_csv'
PASTA_SALVOS = os.path.join(PASTA_DADOS, 'dados_salvos')
ARQUIVO_SALVOS = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_12_meses.csv')
ARQUIVO_SALVOS_MAIS_DE_12_MESES = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_mais_de_12-meses.csv')
ARQUIVO_SALVOS_CA = os.path.join(PASTA_SALVOS, 'top_15_inadimplentes_12_meses_ca.csv')

# Cria pasta de salvos se não existir
if not os.path.exists(PASTA_SALVOS):
    os.makedirs(PASTA_SALVOS)

def formatar_numero_abreviado(valor):
    texto = hu.intword(valor)
    if "million" in texto:
        return texto.replace(" million", "M").replace(".0", "")
    elif "thousand" in texto:
        return texto.replace(" thousand", "k").replace(".0", "")
    return str(valor)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data

def encontrar_arquivo_csv(pasta, nome_arquivo=None):
    """
    Procura por um arquivo .csv na pasta especificada.
    Se nome_arquivo for fornecido, busca por esse arquivo específico.
    Caso contrário, retorna o primeiro .csv que encontrar (exceto 'totais_mensais.csv' se nome não for especificado).
    """
    try:
        arquivos = os.listdir(pasta)
        if nome_arquivo:
            if nome_arquivo in arquivos:
                return os.path.join(pasta, nome_arquivo)
            else:
                return None
        else:
            arquivos_csv = [f for f in arquivos if f.endswith('.csv') and f != 'totais_mensais.csv']
            if arquivos_csv:
                return os.path.join(pasta, arquivos_csv[0])
            else:
                return None
    except FileNotFoundError:
        return None

def carregar_dataframe_csv(caminho):
    try:
        df = pd.read_csv(caminho, sep=',', encoding='latin1')
        # Algumas normalizações básicas que o app original fazia:
        if 'dt_atendimento' in df.columns:
            df['dt_atendimento'] = pd.to_datetime(df['dt_atendimento'], errors='coerce')
        if 'ano' in df.columns:
            df['ano'] = df['ano'].astype(str)
        if 'cd_multi_empresa' in df.columns:
            df['cd_multi_empresa'] = df['cd_multi_empresa'].astype(str)
        if 'sn_fechada' in df.columns:
            df['sn_fechada'] = df['sn_fechada'].astype(str).str.upper()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return None

def salvar_dados_editados(df_editado, destino=ARQUIVO_SALVOS):
    try:
        df_editado.to_csv(destino, index=False, encoding='latin1')
        st.success("Dados salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")

def carregar_dados_salvos(caminho=ARQUIVO_SALVOS):
    try:
        if os.path.exists(caminho):
            return pd.read_csv(caminho, sep=',', encoding='latin1')
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def valida_login():
    """
    Mesma lógica do app original: usa CookieManager para obter usuário e token, checa menuPapel.
    Em caso de permissão negada, redireciona.
    """
    try:
        from streamlit_cookies_manager import CookieManager
    except Exception:
        st.error("Dependência 'streamlit_cookies_manager' não encontrada.")
        return False

    cookies = CookieManager()
    if not cookies.ready():
        st.write("Aguardando inicialização dos cookies...")
        st.stop()

    usuario = cookies.get('username')
    token = cookies.get('token')

    if not usuario or not token:
        st.warning("Usuário ou token de cookie ausentes.")
        return False

    url = f"https://central.hmaterdei.com.br:3001/api/menuPapel/usuario/{usuario}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url=url, headers=headers, verify="./.cert/cert.pem")
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            st.markdown("<meta http-equiv='refresh' content='0; url=https://central.hmaterdei.com.br/'>", unsafe_allow_html=True)
            st.stop()
    except Exception as e:
        st.error(f"Erro ao validar login: {e}")
        return False

    for i in response.json():
        if i.get('CD_PAPEL') == 24 and i.get('CD_SISTEMA') == 10:
            return True
    return False
