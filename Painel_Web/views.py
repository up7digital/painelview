import time
import requests
import socket
import requests
import sseclient
from http import client
from urllib.parse import urlparse
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse

from Administracao.models import tb_Painel, tb_Conexoes
from Administracao.utils.sga_client import SGAClient

class SelecionarPainelView(TemplateView):
    template_name = "Painel_Web/Painel_Home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paineis"] = tb_Painel.objects.filter(status="Ativo").order_by("nome")
        return context

class PainelView(TemplateView):
    template_name = "Painel_Web/Painel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        painel_id = self.request.GET.get("painel")
        painel = get_object_or_404(tb_Painel, id=painel_id)
        context["painel"] = painel

        sga = SGAClient(painel.conexao)
        servicos_ids = painel.servicos_sga or []
        unidade_id = painel.unidade_sga

        try:
            dados = sga.buscar_painel(unidade_id, servicos_ids)
            if not isinstance(dados, list) or not dados:
                context["senha_atual"] = None
                context["historico"] = []
                return context

            senha_atual_api = dados[0]
            estado = processar_regras(painel_id, senha_atual_api)

            context["senha_atual"] = estado["senha_atual"]
            context["historico"] = estado["historico"]

        except Exception as e:
            print("❌ Erro ao consultar painel:", e)
            context["senha_atual"] = None
            context["historico"] = []

        return context

def painel_dados(request):
    painel_id = request.GET.get("painel")
    painel = get_object_or_404(tb_Painel, id=painel_id)

    sga = SGAClient(painel.conexao)
    servicos_ids = painel.servicos_sga or []
    unidade_id = painel.unidade_sga

    try:
        dados = sga.buscar_painel(unidade_id, servicos_ids)
        if not isinstance(dados, list) or not dados:
            return JsonResponse({"senha_atual": None, "historico": []})

        # Pega a senha atual da API
        senha_atual_api = dados[0]

        # Processa regras de histórico
        estado = processar_regras(painel_id, senha_atual_api)

        return JsonResponse({
            "senha_atual": estado["senha_atual"],
            "historico": estado["historico"]
        })

    except Exception as e:
        print("❌ Erro ao consultar dados do painel:", e)
        return JsonResponse({"senha_atual": None, "historico": []})


def processar_regras(painel_id, senha_atual_api):
    key = f"painel_estado_{painel_id}"

    estado = cache.get(key, {
        "senha_atual": None,
        "historico": []
    })

    senha_api = senha_atual_api["senha"]
    numero_local = senha_atual_api.get("numeroLocal")
    local = senha_atual_api.get("local")
    prioridade = senha_atual_api.get("prioridade")

    # Objeto completo da senha
    senha_obj = {
        "senha": senha_api,
        "numeroLocal": numero_local,
        "local": local,
        "prioridade": prioridade
    }

    historico = estado.get("historico", [])
    senha_atual = estado.get("senha_atual")

    # 1) Primeira senha
    if senha_atual is None:
        estado["senha_atual"] = senha_obj
        cache.set(key, estado)
        return estado

    # 2) Mesma senha chamada novamente → remove do histórico, mantém como atual
    if senha_atual["senha"] == senha_api:
        # Remove a senha atual do histórico se por algum motivo estiver lá
        historico = [h for h in historico if h["senha"] != senha_api]
        estado["historico"] = historico
        cache.set(key, estado)
        return estado

    # 3) Nova senha → mover a antiga para histórico, remover do histórico se já existir
    historico = [h for h in historico if h["senha"] != senha_api]  # remove nova senha caso já esteja
    historico.insert(0, senha_atual)  # antiga vai para histórico
    historico = historico[:7]  # limita tamanho

    estado["senha_atual"] = senha_obj
    estado["historico"] = historico

    cache.set(key, estado)
    return estado



def mercure_proxy(request, painel_id):
    painel = get_object_or_404(tb_Painel, id=painel_id)
    conexao = painel.conexao

    # usa diretamente o IP informado na tabela
    resolved_ip = conexao.ip_mercure
    porta = conexao.porta_mercure

    print(f"🌐 Conectando ao Mercure em: {resolved_ip}:{porta}")

    # Monta URL real do Mercure
    mercure_url = f"http://{resolved_ip}:{porta}/.well-known/mercure"

    # Tópico do SGA
    topic = f"/unidades/{painel.unidade_sga}/painel"

    # URL completa para SSE
    full_url = f"{mercure_url}?topic={topic}"
    print("🔗 URL final:", full_url)

    headers = {"Accept": "text/event-stream"}

    try:
        resp = requests.get(full_url, stream=True, timeout=(5, None), headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print("❌ ERRO AO CONECTAR MERCURE:", e)
        return HttpResponse("Erro ao conectar Mercure", status=500)

    client = sseclient.SSEClient(resp)

    def event_stream():
        for event in client.events():
            data = event.data.strip()
            if data:
                yield f"data: {data}\n\n".encode("utf-8")

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # evita buffering no nginx
        },
    )
