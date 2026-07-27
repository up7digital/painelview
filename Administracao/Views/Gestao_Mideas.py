from pathlib import PurePosixPath

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from Administracao.models import MidiaPainel

from .login import active_user_required
from .permissoes import setores_do_usuario, setores_permitidos, usuario_eh_admin


@active_user_required
@permission_required(
    (
        "Administracao.acesso_mideas",
        "Administracao.gerenciar_mideas",
    ),
    raise_exception=True,
)
def gestao_midias(request):
    """Lista as mídias cadastradas para exibição nos painéis."""
    queryset_setores = setores_permitidos(request.user)
    eh_admin = usuario_eh_admin(request.user)
    midias_do_setor = (
        MidiaPainel.objects.all()
        if eh_admin
        else MidiaPainel.objects.filter(setores__in=queryset_setores)
    )
    midias = list(
        midias_do_setor.only(
            "arquivo",
            "texto",
            "tipo",
            "ordem",
            "ativo",
        ).order_by("ordem", "id").distinct()
    )

    for midia in midias:
        midia.nome_arquivo = (
            PurePosixPath(midia.arquivo.name).name
            if midia.arquivo
            else None
        )

    return render(
        request,
        "Administracao/Gestao_Mideas.html",
        {
            "midias": midias,
            "setores_usuario": setores_do_usuario(request.user),
            "eh_admin": eh_admin,
        },
    )
