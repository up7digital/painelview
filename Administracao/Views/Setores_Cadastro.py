from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

from Administracao.models import tb_Setores

from .login import active_user_required


class SetorCadastroForm(forms.ModelForm):
    class Meta:
        model = tb_Setores
        fields = ("nome_setor", "status")


@active_user_required
@permission_required(
    "Administracao.gerenciar_setores",
    raise_exception=True,
)
def setor_cadastro(request):
    """Cadastra um novo setor."""
    if request.method == "POST":
        form = SetorCadastroForm(request.POST)

        if form.is_valid():
            setor = form.save()
            messages.success(request, "Setor cadastrado com sucesso.")
            return redirect(
                "administracao:setor_detalhes",
                setor_id=setor.pk,
            )
    else:
        form = SetorCadastroForm()

    return render(
        request,
        "Administracao/Setores_Cadastro.html",
        {"form": form},
    )
