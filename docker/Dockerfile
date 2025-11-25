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

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Instala as dependências Python no venv
RUN /env/bin/pip install --upgrade pip && \
    /env/bin/pip install -r requirements.txt

# Expõe porta do Django (para acessar via navegador)
EXPOSE 8080

# Comando padrão: roda o servidor de desenvolvimento Django
CMD ["/env/bin/python", "manage.py", "runserver", "0.0.0.0:8080"]
