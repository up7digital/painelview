import json
import time
import requests
from django.core.cache import cache

class SGAClient:
    def __init__(self, conexao):
        self.base_url = conexao.url_origem.rstrip("/")
        self.client_id = conexao.client_id
        self.client_secret = conexao.client_secret
        self.username = conexao.user_sga
        self.password = conexao.pass_sga

        # 🔐 Cache do token
        self.cache_token_key = f"sga_token_{conexao.id}"
        self.cache_exp_key = f"sga_token_exp_{conexao.id}"

    # ----------------------------------------------------
    # 🔐 OBTÉM TOKEN via /api/token (OAuth2 Password Grant)
    # ----------------------------------------------------
    def _get_token(self):
        agora = time.time()

        token = cache.get(self.cache_token_key)
        expira = cache.get(self.cache_exp_key)

        # Token ainda válido → reutiliza
        if token and expira and agora < expira:
            return token
        
        # Token expirado → gerando novo
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

        expira_em = agora + expires - 5  # margem de segurança

        # Salvar token no cache global
        cache.set(self.cache_token_key, token, timeout=expires)
        cache.set(self.cache_exp_key, expira_em, timeout=expires)
        print("🔐 Token gerado/atualizado com SUCESSO (CACHED)")

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
