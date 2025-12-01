# Usa Python 3.12
FROM python:3.12-alpine3.18

# Diretório de trabalho
WORKDIR /app

# Instalações essenciais para compilar pacotes Python comuns
RUN apk update && apk add --no-cache \
    bash \
    curl \
    build-base \
    libffi-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    sqlite-dev \
    openssl-dev

# Cria e ativa ambiente virtual
RUN python -m venv /env

# Copia o projeto inteiro (raiz -> /app)
COPY . /app
COPY entrypoint.sh /app/entrypoint.sh

# Ajusta permissões do entrypoint
RUN chmod +x /app/entrypoint.sh

# Instala dependências
RUN /env/bin/pip install --upgrade pip && \
    /env/bin/pip install -r requirements.txt && \
    /env/bin/pip install gunicorn gevent

# Expondo a porta
EXPOSE 8080

# Entry point para rodar migrations, collectstatic e gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]
