from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render

from Administracao.models import tb_Setores

from .login import active_user_required


class SetorDetalhesForm(forms.ModelForm):
    class Meta:
        model = tb_Setores
        fields = ("nome_setor", "status")


@active_user_required
@permission_required(
    "Administracao.gerenciar_setores",
    raise_exception=True,
)
def setor_detalhes(request, setor_id):
    """Exibe e atualiza os dados de um setor."""
    setor = get_object_or_404(tb_Setores, pk=setor_id)

    if request.method == "POST":
        form = SetorDetalhesForm(request.POST, instance=setor)

        if form.is_valid():
            form.save()
            messages.success(request, "Setor atualizado com sucesso.")
            return redirect(
                "administracao:setor_detalhes",
                setor_id=setor.pk,
            )
    else:
        form = SetorDetalhesForm(instance=setor)

    return render(
        request,
        "Administracao/Setores_Detalhes.html",
        {
            "setor": setor,
            "form": form,
        },
    )
