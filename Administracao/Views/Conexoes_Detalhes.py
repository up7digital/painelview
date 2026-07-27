from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from Administracao.forms import ConexoesForm
from Administracao.models import tb_Conexoes
from .login import active_user_required


@active_user_required
@permission_required(
    "Administracao.gerenciar_conexao",
    raise_exception=True,
)
@require_http_methods(["GET", "POST"])
def conexao_cadastro(request):
    """Cadastra uma nova conexão com o Novo SGA."""
    if request.method == "POST":
        form = ConexoesForm(request.POST)

        if form.is_valid():
            conexao = form.save()
            messages.success(request, "Conexão cadastrada com sucesso.")
            return redirect(
                "administracao:conexao_detalhes",
                conexao_id=conexao.pk,
            )
    else:
        form = ConexoesForm()

    return render(
        request,
        "Administracao/Conexoes_Detalhes.html",
        {
            "form": form,
            "modo_cadastro": True,
        },
    )


@active_user_required
@permission_required(
    "Administracao.gerenciar_conexao",
    raise_exception=True,
)
@require_http_methods(["GET", "POST", "PUT"])
def conexao_detalhes(request, conexao_id):
    """Exibe e atualiza os dados de uma conexão com o Novo SGA."""
    conexao = get_object_or_404(tb_Conexoes, pk=conexao_id)

    if request.method in {"POST", "PUT"}:
        dados = (
            request.POST
            if request.method == "POST"
            else QueryDict(request.body)
        )
        form = ConexoesForm(dados, instance=conexao)

        if form.is_valid():
            form.save()
            messages.success(request, "Conexão atualizada com sucesso.")
            return redirect(
                "administracao:conexao_detalhes",
                conexao_id=conexao.pk,
            )
    else:
        form = ConexoesForm(instance=conexao)

    return render(
        request,
        "Administracao/Conexoes_Detalhes.html",
        {
            "conexao": conexao,
            "form": form,
        },
    )
