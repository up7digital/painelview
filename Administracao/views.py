# Seu app/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from .models import tb_Conexoes # Certifique-se que o path está correto
from .utils.sga_client import SGAClient # Certifique-se que o path está correto


@staff_member_required
def ajax_carregar_unidades(request):
    """
    Carrega as unidades do SGA via AJAX com base na conexão selecionada.
    """
    conexao_id = request.GET.get('conexao_id')
    
    if not conexao_id:
        return JsonResponse({'unidades': []})

    try:
        conexao = get_object_or_404(tb_Conexoes, pk=conexao_id)
        sga = SGAClient(conexao)
        unidades = sga.listar_unidades()

        unidade_choices = [
            {'id': u["id"], 'text': f'{u["id"]} - {u["nome"]}'} 
            for u in unidades
        ]
        
        return JsonResponse({'unidades': unidade_choices})

    except Exception as e:
        print("Erro ao consultar SGA para unidades:", e)
        return JsonResponse({'unidades': [], 'error': str(e)}, status=500)


@staff_member_required
def ajax_carregar_servicos(request):
    """
    Carrega os serviços do SGA via AJAX com base na unidade selecionada.
    """
    conexao_id = request.GET.get('conexao_id')
    unidade_id = request.GET.get('unidade_id')

    if not conexao_id or not unidade_id:
        return JsonResponse({'servicos': []})
    
    try:
        conexao = get_object_or_404(tb_Conexoes, pk=conexao_id)
        sga = SGAClient(conexao)
        servicos = sga.listar_servicos(unidade_id)

        serv_choices = [
            {'id': s["servico"]["id"], 'text': f'{s["sigla"]} - {s["servico"]["nome"]}'} 
            for s in servicos
        ]

        return JsonResponse({'servicos': serv_choices})

    except Exception as e:
        print("Erro ao consultar SGA para serviços:", e)
        return JsonResponse({'servicos': [], 'error': str(e)}, status=500)