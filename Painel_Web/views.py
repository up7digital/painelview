import time
import json
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

from Administracao.models import tb_Painel, tb_Conexoes, MidiaPainel, ConfigPainel
from Administracao.utils.sga_client import SGAClient

from .Views.Personalizacao import personalizacao_css

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
        midias = MidiaPainel.objects.filter(ativo=True).order_by("ordem")
        config = ConfigPainel.objects.first()

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
            context["midias"] = midias
            context["config"] = config

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
    historico = historico[:5]  # limita tamanho

    estado["senha_atual"] = senha_obj
    estado["historico"] = historico

    cache.set(key, estado)
    return estado



def mercure_proxy(request, painel_id):
    print("\n\n🟦🟦🟦 INÍCIO mercure_proxy() 🟦🟦🟦")
    print(f"📌 Requisição recebida. Painel ID = {painel_id}")
    print(f"📌 Método = {request.method} | User = {request.user}")

    painel = get_object_or_404(tb_Painel, id=painel_id)
    conexao = painel.conexao

    resolved_ip = conexao.ip_mercure
    porta = conexao.porta_mercure

    print(f"🌐 Conectando ao Mercure em: {resolved_ip}:{porta}")

    mercure_url = f"http://{resolved_ip}:{porta}/.well-known/mercure"
    topic = f"/unidades/{painel.unidade_sga}/painel"
    full_url = f"{mercure_url}?topic={topic}"

    print(f"🔗 URL final de conexão SSE:\n    {full_url}")
    print(f"📌 Topic usado: {topic}")
    print("📌 Headers enviados:", {"Accept": "text/event-stream"})

    try:
        resp = requests.get(
            full_url,
            stream=True,
            timeout=(5, None),
            headers={"Accept": "text/event-stream"},
        )
        print("🟢 Conexão Mercure OK. Status:", resp.status_code)
        print("📩 Headers da resposta Mercure:", resp.headers)

        resp.raise_for_status()

    except requests.exceptions.Timeout:
        print("⏰ ERRO: Timeout ao conectar no Mercure!")
        return HttpResponse("Timeout Mercure", status=504)

    except requests.exceptions.ConnectionError as e:
        print("🔌 ERRO DE CONEXÃO Mercure:", e)
        return HttpResponse("Erro de conexão", status=502)

    except Exception as e:
        print("❌ ERRO GENÉRICO AO CONECTAR MERCURE:", e)
        return HttpResponse("Erro ao conectar Mercure", status=500)

    print("🟢 Criando SSEClient...")

    try:
        client = sseclient.SSEClient(resp)
        print("🟢 SSEClient criado com sucesso.")
    except Exception as e:
        print("🔥 ERRO ao inicializar SSEClient:", e)
        return HttpResponse("Erro SSE interno", status=500)

    # --------- STREAM DE EVENTOS ----------
    print("📡 Iniciando event_stream()... aguardando eventos.\n")

    def event_stream():
        print("📡 [event_stream] Iniciado...")

        # 🔵 1) KEEP-ALIVE A CADA 15s SE NINGUÉM ENVIAR EVENTO
        last_event = time.time()
        KEEPALIVE_INTERVAL = 15  # segundos

        try:
            for event in client.events():

                # Se passou muito tempo sem evento → envia ping
                now = time.time()
                if now - last_event > KEEPALIVE_INTERVAL:
                    print("🔵 Enviando KEEP-ALIVE (ping)...")
                    yield b": keep-alive\n\n"
                    last_event = now

                print("📨 RECEBIDO EVENTO BRUTO DO MERCURE:")
                print(f"    EVENT.id      = {event.id}")
                print(f"    EVENT.event   = {event.event}")
                print(f"    EVENT.data    = {event.data!r}")
                print("------------------------------------------------")

                data = (event.data or "").strip()
                if not data:
                    print("⚠️ Evento vazio recebido, ignorando.")
                    continue

                # Valida JSON
                try:
                    json.loads(data)
                    print("🟢 JSON válido recebido.")
                except Exception as e:
                    print("❌ JSON INVÁLIDO:", data)
                    print("   Erro:", e)

                print("➡️ Enviando EVENTO REAL ao navegador...\n")
                last_event = time.time()
                yield f"data: {data}\n\n".encode("utf-8")

        except GeneratorExit:
            print("🔻 Cliente fechou o navegador.")
        except Exception as e:
            print("🔥 ERRO SSE:", e)
        finally:
            print("🔚 Finalizando stream SSE.\n\n")


    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
