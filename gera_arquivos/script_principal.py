import os
import pandas as pd
import oracledb
import platform
from dotenv import load_dotenv
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

d=None
if platform.system() != "Windows":
    oracledb.init_oracle_client()
elif platform.system() == "Windows":
    d = r"C:\Oracle\instantclient_19_21"
    oracledb.init_oracle_client(lib_dir=d)

# Importa as queries do arquivo querys.py
from querys import QUERY_1, QUERY_2

def conectar_com_retentativa(max_tentativas=5, tempo_espera=10):
    """
    Tenta conectar ao banco de dados um número limitado de vezes.
    Retorna o objeto 'engine' se a conexão for bem-sucedida, caso contrário, retorna None.
    """
    user = os.getenv('ORACLE_USER')
    password = os.getenv('ORACLE_PASSWORD')
    host = os.getenv('ORACLE_HOST')
    port = os.getenv('ORACLE_PORT')
    service_name = os.getenv('ORACLE_SERVICE_NAME')

    # String de conexão usando SQLAlchemy
    conexao_string = f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service_name}"
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"Tentativa de conexão {tentativa}/{max_tentativas}...")
            engine = create_engine(conexao_string)
            # Tenta se conectar para validar o 'engine'
            with engine.connect() as conn:
                print("Conexão estabelecida com sucesso.")
            return engine
        except SQLAlchemyError as e:
            print(f"Falha na conexão: {e}")
            if tentativa < max_tentativas:
                print(f"Aguardando {tempo_espera} segundos para a próxima tentativa...")
                time.sleep(tempo_espera)
    
    print("\nFalha ao conectar após todas as tentativas. Verifique as configurações e a disponibilidade do banco de dados.")
    return None

def executar_query_e_salvar_csv(query, arquivo_saida, diretorio_saida, engine):
    """
    Função que executa uma query e salva o resultado em um CSV usando um 'engine'
    de conexão já estabelecido.
    """
    try:
        caminho_completo = os.path.join(diretorio_saida, arquivo_saida)

        print(f"Executando a query e buscando os dados...")

        df = pd.read_sql(query, engine)

        print(f"Dados obtidos. Salvando em '{caminho_completo}'...")
        df.to_csv(caminho_completo, index=False, sep=',')

        print(f"Arquivo '{caminho_completo}' criado e atualizado com sucesso.")

    except SQLAlchemyError as e:
        print(f"Ocorreu um erro ao executar a query: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


def main():
    """
    Loop principal que executa as funções de atualização diariamente.
    """
    tempo_de_espera_segundos = 24 * 60 * 60

    diretorio_saida = "../dados_csv"

    if not os.path.exists(diretorio_saida):
        print(f"Diretório '{diretorio_saida}' não encontrado. Criando...")
        os.makedirs(diretorio_saida)
        
    while True:
        print("\n--- Iniciando a atualização ---")
        hora_inicio = datetime.now()
        print(f"Início da execução: {hora_inicio.strftime('%Y-%m-%d %H:%M:%S')}")

        # Tenta conectar ao banco de dados com retentativa
        engine = conectar_com_retentativa()
        
        if engine:
            # Se a conexão for bem-sucedida, executa as queries
            executar_query_e_salvar_csv(QUERY_1, 'dados.csv', diretorio_saida, engine)

            print("-" * 20)

            executar_query_e_salvar_csv(QUERY_2, 'totais_mensais.csv', diretorio_saida, engine)
            
            # Fecha o 'engine' para liberar a conexão
            engine.dispose()
        else:
            print("Não foi possível conectar ao banco de dados. Tentando novamente na próxima execução.")
        
        print("\n--- Atualização completa ---")
        
        print(f"Próxima atualização em 24 horas. Aguardando...")
        time.sleep(tempo_de_espera_segundos)

if __name__ == "__main__":
    main()