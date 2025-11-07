# Usa uma imagem oficial do Python 3.13
FROM python:3.13-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

RUN echo "deb http://deb.debian.org/debian bookworm main non-free contrib" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main non-free contrib" >> /etc/apt/sources.list

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    supervisor \
    libaio1 \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/2118000/instantclient-basiclite-linux.x64-21.18.0.0.0dbru.zip \
    && unzip instantclient-basiclite.zip -d /opt/oracle \
    && rm instantclient-basiclite.zip \
    && echo "/opt/oracle/instantclient_21_18" > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

# Definir variáveis de ambiente para o Oracle Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_18
ENV ORACLE_HOME=/opt/oracle/instantclient_21_18

# Copia o arquivo de dependências e instala as bibliotecas
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o arquivo de configuração do supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copia todo o restante do projeto para o diretório de trabalho
COPY . .

# Define os diretórios de log para o supervisor
RUN mkdir -p /var/log/supervisor

# Expõe a porta que o Streamlit irá usar
EXPOSE 3090

# Comando padrão para iniciar o supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]