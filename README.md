# Painel View

Painel de exibição de senhas integrado ao Novo SGA. O projeto tem duas áreas principais:

- **Administracao**: conexões, painéis, mídias, setores, usuários e permissões.
- **Painel_Web**: seleção e exibição das senhas, atualizações ao vivo e vocalização.

## Requisitos

- Python 3.12 (o projeto usa Django 5.2).
- Acesso a uma instância do Novo SGA para carregar senhas e, se utilizado, a um servidor Mercure para atualizações em tempo real.

## Instalação local

No PowerShell, a partir da pasta do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Gere uma chave secreta para o ambiente local e coloque o resultado em `DJANGO_SECRET_KEY` no arquivo `.env`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

O arquivo `.env` é local e não deve ser enviado ao Git.

## Banco e primeiro acesso

Por padrão, o projeto usa SQLite em `db.sqlite3`. Crie as tabelas e a conta administrativa:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

Os grupos e permissões definidos pelo projeto são sincronizados durante as migrações. Entre com a conta criada e cadastre a conexão do Novo SGA em **Configurações → Conexões**, preenchendo URL, credenciais de API e endereço/porta do Mercure. O sistema não cria mais conexões com credenciais embutidas no código.

## Executar

```powershell
python manage.py runserver 127.0.0.1:8000
```

Abra <http://127.0.0.1:8000/> para selecionar setor e painel. O admin do Django fica em <http://127.0.0.1:8000/admin/>.

`runserver` serve para desenvolvimento local. Em produção, use um servidor ASGI, HTTPS e um servidor web ou serviço apropriado para arquivos estáticos e de mídia. Não exponha `runserver` diretamente à Internet.

## Variáveis de ambiente

As opções são lidas do ambiente e, localmente, do arquivo `.env`:

| Variável | Uso |
| --- | --- |
| `DJANGO_SECRET_KEY` | Chave secreta do Django. Obrigatória quando `DJANGO_DEBUG=false`. |
| `DJANGO_DEBUG` | Ativa depuração; padrão local `true`. Em produção, use `false`. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por vírgulas, sem protocolo. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origens confiáveis separadas por vírgulas, com `https://` ou `http://`. |
| `DJANGO_TIME_ZONE` | Fuso horário; padrão `America/Fortaleza`. |

Exemplo de produção:

```dotenv
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=uma-chave-longa-e-aleatoria
DJANGO_ALLOWED_HOSTS=painel.exemplo.org
DJANGO_CSRF_TRUSTED_ORIGINS=https://painel.exemplo.org
DJANGO_TIME_ZONE=America/Fortaleza
```

Proteja também o acesso ao banco, pois os dados de conexão com o Novo SGA são armazenados nele.

## Antes de publicar

- Não envie `.env`, bancos de dados, arquivos de mídia ou chaves para o repositório.
- Este código já conteve credenciais reais de uma conexão do Novo SGA. Antes de publicar, revogue e gere novos valores para a senha, `client_id` e `client_secret` expostos. Se esses valores já estiveram em commits anteriores, removê-los do código atual não apaga o histórico Git; limpe o histórico antes de tornar o repositório público.
- Em produção, use `DJANGO_DEBUG=false`, uma chave secreta nova e forte, hosts/origens explícitos e HTTPS.
