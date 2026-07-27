import hashlib
import json

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from Administracao.models import ConfigPainel, MidiaPainel, tb_Painel
from Administracao.utils.sga_client import SGAClient

from .Vocalizacao import preparar_vocalizacao


def _midias_do_painel(painel):
    if painel.setor_id is None:
        return MidiaPainel.objects.none()

    return (
        MidiaPainel.objects.filter(
            ativo=True,
            setores=painel.setor_id,
        )
        .distinct()
        .order_by("ordem", "id")
    )


def _config_do_painel(painel):
    if painel.setor_id is None:
        return ConfigPainel.objects.first()

    return (
        ConfigPainel.objects.filter(setor_id=painel.setor_id)
        .order_by("id")
        .first()
    )


def _revisao_midias(midias, config):
    dados = {
        "midias": [
            {
                "id": midia.pk,
                "tipo": midia.tipo,
                "arquivo": midia.arquivo.name if midia.arquivo else "",
                "texto": midia.texto or "",
                "texto_tamanho_fonte": midia.texto_tamanho_fonte,
                "texto_cor": midia.texto_cor,
                "texto_alinhamento": midia.texto_alinhamento,
                "ordem": midia.ordem,
                "exibir_lateral": midia.exibir_lateral,
                "exibir_popup": midia.exibir_popup,
            }
            for midia in midias
        ],
        "config": {
            "tempo_exibicao_imagem": (
                config.tempo_exibicao_imagem if config else 5
            ),
            "tempo_popup": config.tempo_popup if config else 10,
        },
    }
    serializado = json.dumps(
        dados,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


class PainelView(TemplateView):
    template_name = "Painel_Web/Painel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        painel_id = self.request.GET.get("painel")
        painel = get_object_or_404(tb_Painel, id=painel_id)

        context["painel"] = painel
        context["midias"] = _midias_do_painel(painel)
        context["config"] = _config_do_painel(painel)
        context["vocalizacao_config"] = {
            "voz": painel.voz_vocalizacao,
            "velocidade": float(painel.velocidade_vocalizacao),
            "tom": float(painel.tom_vocalizacao),
        }
        context["senha_atual"] = None
        context["historico"] = []

        sga = SGAClient(painel.conexao)
        servicos_ids = painel.servicos_sga or []
        unidade_id = painel.unidade_sga

        try:
            dados = sga.buscar_painel(unidade_id, servicos_ids)

            if isinstance(dados, list) and dados:
                senha_atual_api = dados[0]
                estado = processar_regras(painel_id, senha_atual_api)

                context["senha_atual"] = estado["senha_atual"]
                context["historico"] = estado["historico"]

        except Exception as error:
            print("❌ Erro ao consultar painel:", error)

        return context


@require_GET
def painel_midias(request):
    painel = get_object_or_404(
        tb_Painel.objects.select_related("setor"),
        pk=request.GET.get("painel"),
    )
    midias = list(_midias_do_painel(painel))
    config = _config_do_painel(painel)
    revisao = _revisao_midias(midias, config)

    if request.GET.get("revisao") == revisao:
        return JsonResponse(
            {
                "alterado": False,
                "revisao": revisao,
            }
        )

    contexto = {"midias": midias}
    return JsonResponse(
        {
            "alterado": True,
            "revisao": revisao,
            "lateral_html": render_to_string(
                "Painel_Web/partials/midias_laterais_itens.html",
                contexto,
                request=request,
            ),
            "popup_html": render_to_string(
                "Painel_Web/partials/midias_popup_itens.html",
                contexto,
                request=request,
            ),
            "tempo_imagem_ms": (
                config.tempo_exibicao_imagem if config else 5
            ) * 1000,
            "tempo_popup_ms": (
                config.tempo_popup if config else 10
            ) * 1000,
        }
    )


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

        senha_atual_api = dados[0]
        estado = processar_regras(painel_id, senha_atual_api)
        chamadas = [_normalizar_chamada(item) for item in dados]

        return JsonResponse(
            {
                "senha_atual": estado["senha_atual"],
                "historico": estado["historico"],
                "chamadas": chamadas,
            }
        )

    except Exception as error:
        print("❌ Erro ao consultar dados do painel:", error)
        return JsonResponse({"senha_atual": None, "historico": []})


def processar_regras(painel_id, senha_atual_api):
    key = f"painel_estado_{painel_id}"

    estado = cache.get(
        key,
        {
            "senha_atual": None,
            "historico": [],
        },
    )

    senha_obj = _normalizar_chamada(senha_atual_api)
    senha_api = senha_obj["senha"]

    historico = estado.get("historico", [])
    senha_atual = estado.get("senha_atual")

    if senha_atual is None:
        estado["senha_atual"] = senha_obj
        cache.set(key, estado)
        return estado

    if senha_atual["senha"] == senha_api:
        historico = [item for item in historico if item["senha"] != senha_api]
        estado["senha_atual"] = senha_obj
        estado["historico"] = historico
        cache.set(key, estado)
        return estado

    historico = [item for item in historico if item["senha"] != senha_api]
    historico.insert(0, senha_atual)
    historico = historico[:5]

    estado["senha_atual"] = senha_obj
    estado["historico"] = historico

    cache.set(key, estado)
    return estado


def _normalizar_chamada(chamada):
    senha = chamada["senha"]
    numero_local = chamada.get("numeroLocal")
    local = chamada.get("local")

    return {
        "id": chamada.get("id"),
        "senha": senha,
        "nomeCliente": chamada.get("nomeCliente"),
        "numeroLocal": numero_local,
        "local": local,
        "prioridade": chamada.get("prioridade"),
        "vocalizacao": preparar_vocalizacao(
            senha,
            local,
            numero_local,
            nome_cliente=chamada.get("nomeCliente"),
        ),
    }
