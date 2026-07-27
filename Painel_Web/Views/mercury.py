import json
import time

import requests
import sseclient
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from Administracao.models import tb_Painel


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
        response = requests.get(
            full_url,
            stream=True,
            timeout=(5, None),
            headers={"Accept": "text/event-stream"},
        )
        print("🟢 Conexão Mercure OK. Status:", response.status_code)
        print("📩 Headers da resposta Mercure:", response.headers)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("⏰ ERRO: Timeout ao conectar no Mercure!")
        return HttpResponse("Timeout Mercure", status=504)
    except requests.exceptions.ConnectionError as error:
        print("🔌 ERRO DE CONEXÃO Mercure:", error)
        return HttpResponse("Erro de conexão", status=502)
    except Exception as error:
        print("❌ ERRO GENÉRICO AO CONECTAR MERCURE:", error)
        return HttpResponse("Erro ao conectar Mercure", status=500)

    print("🟢 Criando SSEClient...")

    try:
        sse_client = sseclient.SSEClient(response)
        print("🟢 SSEClient criado com sucesso.")
    except Exception as error:
        print("🔥 ERRO ao inicializar SSEClient:", error)
        return HttpResponse("Erro SSE interno", status=500)

    print("📡 Iniciando event_stream()... aguardando eventos.\n")

    def event_stream():
        print("📡 [event_stream] Iniciado...")

        last_event = time.time()
        keepalive_interval = 15

        try:
            for event in sse_client.events():
                now = time.time()
                if now - last_event > keepalive_interval:
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

                try:
                    json.loads(data)
                    print("🟢 JSON válido recebido.")
                except Exception as error:
                    print("❌ JSON INVÁLIDO:", data)
                    print("   Erro:", error)

                print("➡️ Enviando EVENTO REAL ao navegador...\n")
                last_event = time.time()
                yield f"data: {data}\n\n".encode("utf-8")
        except GeneratorExit:
            print("🔻 Cliente fechou o navegador.")
        except Exception as error:
            print("🔥 ERRO SSE:", error)
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
