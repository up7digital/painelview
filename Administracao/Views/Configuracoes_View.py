from django.shortcuts import render

from .login import active_user_required


@active_user_required
def configuracoes(request):
    """Exibe o ponto de entrada das configurações administrativas."""
    return render(request, "Administracao/Configuracoes.html")
