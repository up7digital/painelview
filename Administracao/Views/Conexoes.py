from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from Administracao.models import tb_Conexoes
from .login import active_user_required


@active_user_required
@permission_required(
    "Administracao.gerenciar_conexao",
    raise_exception=True,
)
@require_GET
def conexoes(request):
    """Lista as conexões cadastradas com o Novo SGA."""
    conexoes_cadastradas = (
        tb_Conexoes.objects.only("nome_conexao", "url_origem")
        .order_by("nome_conexao")
    )

    return render(
        request,
        "Administracao/Conexoes.html",
        {"conexoes": conexoes_cadastradas},
    )
