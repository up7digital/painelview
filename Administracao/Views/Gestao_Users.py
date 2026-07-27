from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from .login import active_user_required


@active_user_required
@permission_required(
    "auth.acesso_usuarios",
    raise_exception=True,
)
def gestao_users(request):
    """Lista todos os usuários cadastrados no Django."""
    User = get_user_model()
    usuarios = User.objects.prefetch_related(
        "groups",
        "vinculos_setores__setor",
    ).order_by("username")

    for usuario in usuarios:
        usuario.setores_vinculados = [
            vinculo.setor
            for vinculo in usuario.vinculos_setores.all()
            if vinculo.setor is not None
        ]

    return render(
        request,
        "Administracao/Gestao_Users.html",
        {"usuarios": usuarios},
    )
