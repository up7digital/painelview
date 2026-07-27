from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from Administracao.models import tb_Painel
from .login import active_user_required


@active_user_required
@permission_required(
    "Administracao.gerenciar_paineis",
    raise_exception=True,
)
def gestao_paineis(request):
    """Lista os painéis cadastrados e seus respectivos status."""
    paineis = tb_Painel.objects.only("nome", "status").order_by("nome")

    return render(
        request,
        "Administracao/Gestao_Paineis.html",
        {"paineis": paineis},
    )
