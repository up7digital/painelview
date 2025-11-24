import requests
import time


class SGAClient:
    def __init__(self, conexao):
        self.base_url = conexao.url_origem.rstrip("/")
        self.client_id = conexao.client_id
        self.client_secret = conexao.client_secret
        self.username = conexao.user_sga
        self.password = conexao.pass_sga

        # 🔐 Cache do token
        self._token = None
        self._token_expira = 0

    # ----------------------------------------------------
    # 🔐 OBTÉM TOKEN via /api/token (OAuth2 Password Grant)
    # ----------------------------------------------------
    def _get_token(self):
        agora = time.time()

        # Token ainda válido → usar cache
        if self._token and agora < self._token_expira:
            return self._token

        url = f"{self.base_url}/api/token"
        print("🔎 Endpoint TOKEN:", url)

        payload = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        resp = requests.post(url, data=payload, headers=headers)
        resp.raise_for_status()

        data = resp.json()

        token = data.get("access_token")
        expires = data.get("expires_in", 300)

        if not token:
            raise ValueError("⚠️ Nenhum token retornado pelo endpoint /api/token")

        # Cacheia token com margem de segurança
        self._token = token
        self._token_expira = agora + int(expires) - 5

        print("🔐 Token gerado/atualizado com sucesso")
        return token

    # Cabeçalho com Bearer Token
    def _headers(self):
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Accept": "application/json",
        }

    # ----------------------------------------------
    # 🔹 LISTAR UNIDADES
    # ----------------------------------------------
    def listar_unidades(self):
        url = f"{self.base_url}/api/unidades"
        print("➡️ Buscando unidades:", url)

        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()

    # ----------------------------------------------
    # 🔹 LISTAR SERVIÇOS
    # ----------------------------------------------
    def listar_servicos(self, id_unidade):
        url = f"{self.base_url}/api/unidades/{id_unidade}/servicos"
        print("➡️ Buscando serviços:", url)

        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()

    # ----------------------------------------------
    # 🔥 BUSCAR SENHAS DO PAINEL
    # ----------------------------------------------
    def buscar_painel(self, id_unidade, servicos):
        servicos_str = ",".join(map(str, servicos))
        url = f"{self.base_url}/api/unidades/{id_unidade}/painel?servicos={servicos_str}"

        print("📡 Consultando Painel:", url)

        r = requests.get(url, headers=self._headers())
        r.raise_for_status()

        return r.json()
