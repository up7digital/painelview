from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from Administracao.models import tb_Setores

from .login import active_user_required


@active_user_required
@permission_required(
    "Administracao.gerenciar_setores",
    raise_exception=True,
)
def gestao_setores(request):
    """Lista os setores cadastrados."""
    setores = tb_Setores.objects.only("nome_setor").order_by("nome_setor")

    return render(
        request,
        "Administracao/Gestao_Setores.html",
        {"setores": setores},
    )
