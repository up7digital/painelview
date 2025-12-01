# Usa Python 3.12
FROM python:3.12-alpine3.18

# Diretório de trabalho
WORKDIR /app

# Instalações essenciais para compilar pacotes Python comuns
RUN apk update && apk add --no-cache \
    bash \
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

# Instala dependências
RUN /env/bin/pip install --upgrade pip && \
    /env/bin/pip install -r requirements.txt && \
    /env/bin/pip install gunicorn gevent

EXPOSE 8080

# Comando padrão: iniciar Gunicorn usando gevent
CMD ["/env/bin/gunicorn", "PainelView.wsgi:application", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "3", \
     "--worker-class", "gevent", \
     "--timeout", "0", \
     "--keep-alive", "65"]
